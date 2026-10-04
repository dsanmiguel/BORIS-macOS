BORIS (Behavioral Observation Research Interactive Software)
===============================================================


![BORIS logo](https://github.com/olivierfriard/BORIS/blob/master/boris/icons/logo_boris.png?raw=true)

## About This Fork

This repository is a macOS-focused fork of the BORIS project. It is intended to address macOS-specific issues related to `mpv`, IPC control, and playback behavior.

The goal of this fork is to keep changes as small as possible while improving BORIS on macOS, rather than diverging substantially from upstream. This fork is based on official BORIS 9.15.0 (the fork version 9.15.0.x corresponds to BORIS 9.15.0), with the following macOS changes:

- **Video inside the BORIS window.** The video is displayed in the player panels of the BORIS window (libmpv with the mpv render API and OpenGL) instead of separate mpv windows. Mouse clicks, double-click zoom, Ctrl/Cmd+scroll zoom, Shift+scroll pan, frame extraction and geometric measurements work like on Windows and Linux.
- **Rearrangeable panels.** The player, events, ethogram, subjects and information panels can be moved, floated and docked again like on Windows (use *Tools > Lock dockwidgets* to lock them).
- **Arrow keys work for frame-by-frame navigation.** macOS reports the arrow keys with the numeric keypad modifier, so BORIS showed *Key not assigned (Num+Left)* instead of going to the previous / next frame (and Up / Down did not jump backward / forward).
- **Show / hide columns** of the Ethogram, Subjects and Events panels: right-click on the header of a table (or choose *Configure columns* in the right-click menu of the table) and check / uncheck the columns. The choice is kept when BORIS is restarted.
- **No more freezes during scoring in IPC mode.** mpv's output was sent to a pipe that was never read; when the pipe was full mpv stopped and BORIS waited forever. mpv's messages now go to a log file (`/tmp/mpvsocket<N>.log`) and BORIS no longer waits forever for an unresponsive mpv.

### Requirements

Install mpv (which includes libmpv) and FFmpeg with [Homebrew](https://brew.sh):

```
brew install mpv ffmpeg
```

If libmpv is not found, BORIS falls back to the previous mode with the video in separate mpv windows (mpv IPC mode). This mode can also be forced with the `--ipc` (`-i`) option.

With hardware decoding (*Preferences > MPV player hardware video decoding* set to `auto` or `auto-safe`) BORIS uses VideoToolbox with copy-back (`auto-copy`), because frame extraction and geometric measurements cannot use the frames of the zero-copy mode.

If you encounter a problem specific to this fork, please open an issue in this repository and I will do my best to resolve it quickly.

Unless noted otherwise, the documentation below is reproduced from the official BORIS repository:
https://github.com/olivierfriard/BORIS/

---

BORIS is an easy-to-use event logging software for video/audio coding or live observations.

BORIS is a free and open-source software available for GNU/Linux, Windows and macOS.

It provides also some analysis tools like time budget and some plotting functions.

<!-- The BO-RIS paper has more than [![BORIS citations counter](https://penelope.unito.it/friard/boris_scopus_citations.png) citations](https://www.boris.unito.it/citations) in peer-reviewed scientific publications. -->


The BORIS paper has more than 2673 citations in peer-reviewed scientific publications.




See the official [BORIS web site](https://www.boris.unito.it).

<a href="https://www.boris.unito.it" target="_blank"><img alt="Website" src="https://img.shields.io/website?url=https%3A%2F%2Fwww.boris.unito.it"></a>
<a href="https://www.boris.unito.it/user_guide/" target="_blank"><img alt="User guide" src="https://img.shields.io/badge/Documentation-orange"></a>
[![Python web site](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org)
![Python versions](https://img.shields.io/pypi/pyversions/boris-behav-obs)
![BORIS license](https://img.shields.io/pypi/l/boris-behav-obs)
[![PyPI version](https://img.shields.io/pypi/v/boris-behav-obs.svg)](https://pypi.org/project/boris-behav-obs/)

[![Number of downloads](https://static.pepy.tech/personalized-badge/boris-behav-obs?period=total&units=international_system&left_color=black&right_color=orange&left_text=Downloads)](https://pepy.tech/project/boris-behav-obs)
![commit-activity](https://img.shields.io/github/commit-activity/m/olivierfriard/BORIS)
![GitHub last commit](https://img.shields.io/github/last-commit/olivierfriard/BORIS)

![BORIS scopus citations badge](https://penelope.unito.it/friard/boris_scopus_citations.svg)


![GitHub Repo stars](https://img.shields.io/github/stars/olivierfriard/BORIS?style=flat&label=Stars)
[![Please Star](https://img.shields.io/badge/
