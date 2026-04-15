import json
import sys
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "boris"))

import ipc_mpv


class FakeSocket:
    def __init__(self, recv_chunks):
        self.recv_chunks = list(recv_chunks)
        self.sent_messages = []
        self.closed = False

    def settimeout(self, _timeout):
        return

    def sendall(self, data):
        self.sent_messages.append(data)

    def recv(self, _size):
        if not self.recv_chunks:
            return b""
        return self.recv_chunks.pop(0)

    def close(self):
        self.closed = True


def make_player(fake_socket):
    player = ipc_mpv.IPC_MPV.__new__(ipc_mpv.IPC_MPV)
    player.socket_path = "/tmp/mpvsocket-test"
    player.process = None
    player._sock = None
    player._recv_buffer = b""
    player._next_request_id = 1
    player._pending_responses = {}
    player._socket_lock = threading.RLock()

    connect_calls = {"count": 0}

    def connect_socket():
        if player._sock is None:
            connect_calls["count"] += 1
            player._sock = fake_socket
        return True

    player._connect_socket = connect_socket
    return player, connect_calls


def test_send_command_reuses_socket_and_matches_request_ids():
    fake_socket = FakeSocket(
        [
            b'{"event":"idle"}\n{"request_id":1,',
            b'"error":"success","data":1}\n{"request_id":2,"error":"success","data":2}\n',
        ]
    )
    player, connect_calls = make_player(fake_socket)

    assert player.send_command({"command": ["frame-step"]}) == 1
    assert player.send_command({"command": ["frame-back-step"]}) == 2
    assert connect_calls["count"] == 1
    assert len(fake_socket.sent_messages) == 2

    first_command = json.loads(fake_socket.sent_messages[0].decode("utf-8").strip())
    second_command = json.loads(fake_socket.sent_messages[1].decode("utf-8").strip())

    assert first_command["request_id"] == 1
    assert second_command["request_id"] == 2


def test_send_command_buffers_multiple_messages_until_newline():
    fake_socket = FakeSocket(
        [
            b'{"request_id":1,"error":"success","data":"playlist"}\n{"event":"tick"}\n',
        ]
    )
    player, _connect_calls = make_player(fake_socket)

    assert player.send_command({"command": ["get_property", "playlist"]}) == "playlist"
    assert player._recv_buffer == b'{"event":"tick"}\n'


def test_wait_until_playing_polls_until_duration_available(monkeypatch):
    player = ipc_mpv.IPC_MPV.__new__(ipc_mpv.IPC_MPV)
    player.LOAD_TIMEOUT = 0.2
    player.RETRY_DELAY = 0.001

    state = {"calls": 0}

    def duration(_self):
        state["calls"] += 1
        return None if state["calls"] < 3 else 12.5

    monkeypatch.setattr(ipc_mpv.IPC_MPV, "playlist_count", property(lambda _self: 1))
    monkeypatch.setattr(ipc_mpv.IPC_MPV, "duration", property(duration))

    assert player.wait_until_playing() is True
