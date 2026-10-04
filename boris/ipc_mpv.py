"""
BORIS
Behavioral Observation Research Interactive Software
Copyright 2012-2026 Olivier Friard

This file is part of BORIS.

  BORIS is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 3 of the License, or
  any later version.

  BORIS is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program; if not see <http://www.gnu.org/licenses/>.

"""

import json
import logging
import socket
import subprocess

import config as cfg

logger = logging.getLogger(__name__)


class IPC_MPV:
    """
    class for managing mpv through Inter Process Communication (IPC)
    """

    media_durations: list = []
    cumul_media_durations: list = []
    fps: list = []
    _pause: bool = False

    # maximum time in seconds for a response of mpv
    RESPONSE_TIMEOUT = 5

    def __init__(self, socket_path: str = cfg.MPV_SOCKET, parent=None):
        # print(f"{parent=}")
        self.socket_path = socket_path
        self.log_path = socket_path + ".log"
        self.process = None
        # self.sock = None
        self.init_mpv()
        # self.init_socket()

    def init_mpv(self):
        """
        Start mpv process and embed it in the PySide6 application.
        """
        logger.info(f"Start mpv ipc process (mpv messages in {self.log_path})")
        # The output of mpv must not be sent to a pipe that is never read:
        # when the pipe buffer is full (64 KB on macOS) mpv blocks and the video freezes.
        # --quiet: no status line (AV: 00:12:34 / 00:38:30 ...) written every second
        with open(self.log_path, "w") as log_file:
            self.process = subprocess.Popen(
                [
                    "mpv",
                    "--ontop",
                    "--no-border",
                    "--osc=no",  # no on screen commands
                    "--quiet",
                    "--input-ipc-server=" + self.socket_path,
                    # "--wid=" + str(int(self.winId())),  # Embed in the widget
                    "--idle=yes",  # Keeps mpv running with no video
                    "--keep-open=always",
                    "--input-default-bindings=no",
                    "--input-vo-keyboard=no",
                ],
                stdin=subprocess.DEVNULL,
                stdout=log_file,
                stderr=subprocess.STDOUT,
            )

    def log_tail(self, max_lines: int = 20) -> str:
        """
        returns the last messages of mpv
        """
        try:
            with open(self.log_path, errors="replace") as f_in:
                return "".join(f_in.readlines()[-max_lines:])
        except OSError:
            return ""

    def send_command(self, command):
        """
        Send a JSON command to the mpv IPC server.
        """
        # print(f"send command: {command}")
        try:
            # Create a Unix socket
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
                # do not wait forever if mpv is not responding
                client.settimeout(self.RESPONSE_TIMEOUT)
                # Connect to the MPV IPC server
                client.connect(self.socket_path)
                # Send the JSON command
                # print(f"{json.dumps(command).encode('utf-8')=}")
                client.sendall(json.dumps(command).encode("utf-8") + b"\n")
                # Receive the response
                response_data = self._read_response(client)

                # print(f"{response_data=}")
                if response_data["error"] != "success":
                    logging.warning(f"send command: {command} response data: {response_data}")
                # Return the 'data' field which contains the playback position
                return response_data.get("data")
        except FileNotFoundError:
            logger.critical("Error: Socket file not found.")
        except TimeoutError:
            logger.critical(f"mpv did not respond to {command} in {self.RESPONSE_TIMEOUT} s")
        except Exception as e:
            logger.critical(f"An error occurred: {e}")
        return None

    def _read_response(self, client) -> dict:
        """
        Read the response of mpv to a command.
        The messages of mpv are JSON objects separated by newlines and can be split in several packets.
        The events sent by mpv to all clients (without "error" key) are skipped.
        """
        buffer = b""
        while True:
            while b"\n" in buffer:
                line, buffer = buffer.split(b"\n", 1)
                if not line.strip():
                    continue
                message = json.loads(line.decode("utf-8"))
                if "error" in message:
                    return message
            chunk = client.recv(4096)
            if not chunk:
                raise ConnectionError("mpv closed the connection")
            buffer += chunk

    @property
    def time_pos(self):
        time_pos = self.send_command({"command": ["get_property", "time-pos"]})
        return time_pos

    @property
    def duration(self):
        duration_ = self.send_command({"command": ["get_property", "duration"]})
        return duration_

    @property
    def video_zoom(self):
        return self.send_command({"command": ["get_property", "video-zoom"]})

    @video_zoom.setter
    def video_zoom(self, value):
        self.send_command({"command": ["set_property", "video-zoom", value]})
        return

    @property
    def pause(self):
        return self.send_command({"command": ["get_property", "pause"]})

    @pause.setter
    def pause(self, value):
        return self.send_command({"command": ["set_property", "pause", value]})

    @property
    def mute(self):
        return self.send_command({"command": ["get_property", "mute"]})

    @mute.setter
    def mute(self, value):
        return self.send_command({"command": ["set_property", "mute", value]})

    @property
    def estimated_frame_number(self):
        return self.send_command({"command": ["get_property", "estimated-frame-number"]})

    def stop(self):
        self.send_command({"command": ["stop"]})
        return

    @property
    def playlist(self):
        return self.send_command({"command": ["get_property", "playlist"]})

    def playlist_next(self):
        self.send_command({"command": ["playlist-next"]})
        return

    def playlist_prev(self):
        self.send_command({"command": ["playlist-prev"]})
        return

    @property
    def playlist_pos(self):
        return self.send_command({"command": ["get_property", "playlist-pos"]})

    @playlist_pos.setter
    def playlist_pos(self, value):
        return self.send_command({"command": ["set_property", "playlist-pos", value]})

    @property
    def playlist_count(self):
        return self.send_command({"command": ["get_property", "playlist-count"]})

    def playlist_append(self, media):
        return self.send_command({"command": ["loadfile", media, "append"]})

    def wait_until_playing(self):
        return

    def seek(self, value, mode: str):
        self.send_command({"command": ["seek", value, mode]})
        return

    @property
    def playback_time(self):
        playback_time_ = self.send_command({"command": ["get_property", "playback-time"]})
        return playback_time_

    def frame_step(self):
        self.send_command({"command": ["frame-step"]})
        return

    def frame_back_step(self):
        self.send_command({"command": ["frame-back-step"]})
        return

    def screenshot_to_file(self, value):
        self.send_command({"command": ["screenshot-to-file", value, "video"]})
        return

    @property
    def speed(self):
        return self.send_command({"command": ["get_property", "speed"]})

    @speed.setter
    def speed(self, value):
        self.send_command({"command": ["set_property", "speed", value]})
        return

    @property
    def video_rotate(self):
        return self.send_command({"command": ["get_property", "video-rotate"]})

    @video_rotate.setter
    def video_rotate(self, value):
        self.send_command({"command": ["set_property", "video-rotate", value]})
        return

    @property
    def sub_visibility(self):
        return self.send_command({"command": ["get_property", "sub-visibility"]})

    @sub_visibility.setter
    def sub_visibility(self, value):
        self.send_command({"command": ["set_property", "sub-visibility", value]})
        return

    @property
    def brightness(self):
        return self.send_command({"command": ["get_property", "brightness"]})

    @brightness.setter
    def brightness(self, value):
        self.send_command({"command": ["set_property", "brightness", value]})
        return

    @property
    def contrast(self):
        return self.send_command({"command": ["get_property", "contrast"]})

    @contrast.setter
    def contrast(self, value):
        self.send_command({"command": ["set_property", "contrast", value]})
        return

    @property
    def saturation(self):
        return self.send_command({"command": ["get_property", "saturation"]})

    @saturation.setter
    def saturation(self, value):
        self.send_command({"command": ["set_property", "saturation", value]})
        return

    @property
    def gamma(self):
        return self.send_command({"command": ["get_property", "gamma"]})

    @gamma.setter
    def gamma(self, value):
        self.send_command({"command": ["set_property", "gamma", value]})
        return

    @property
    def hue(self):
        return self.send_command({"command": ["get_property", "hue"]})

    @hue.setter
    def hue(self, value):
        self.send_command({"command": ["set_property", "hue", value]})
        return

    @property
    def container_fps(self):
        return self.send_command({"command": ["get_property", "container-fps"]})

    @property
    def width(self):
        return self.send_command({"command": ["get_property", "width"]})

    @property
    def height(self):
        return self.send_command({"command": ["get_property", "height"]})

    @property
    def video_format(self):
        return self.send_command({"command": ["get_property", "video-format"]})

    @property
    def deinterlace(self):
        return self.send_command({"command": ["get_property", "deinterlace"]})

    @deinterlace.setter
    def deinterlace(self, value):
        self.send_command({"command": ["set_property", "deinterlace", value]})
        return

    @property
    def audio_bitrate(self):
        return self.send_command({"command": ["get_property", "audio-bitrate"]})

    @property
    def eof_reached(self):
        return self.send_command({"command": ["get_property", "eof-reached"]})

    @property
    def core_idle(self):
        return self.send_command({"command": ["get_property", "core-idle"]})

    @property
    def video_pan_x(self):
        return self.send_command({"command": ["get_property", "video-pan-x"]})

    @video_pan_x.setter
    def video_pan_x(self, value):
        self.send_command({"command": ["set_property", "video-pan-x", value]})
        return

    @property
    def video_pan_y(self):
        return self.send_command({"command": ["get_property", "video-pan-y"]})

    @video_pan_y.setter
    def video_pan_y(self, value):
        self.send_command({"command": ["set_property", "video-pan-y", value]})
        return

    """
    @property
    def xxx(self):
        return self.send_command({"command": ["get_property", "xxx"]})

    @xxx.setter
    def xxx(self, value):
        self.send_command({"command": ["set_property", "xxx", value]})
        return
    """
