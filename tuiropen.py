#!/usr/bin/env python
"""
tuiropen is a command-line utility for opening URLs from tuir.

This script allows users to open image/video URLs from tuir in their default
image viewer or video player.

* Tuir Original Author: [@ajak](https://gitlab.com/ajak/tuir/)

usage:
    tuiropen <url>

arguments:
    url: the URL of the media file to open

example:
    $ tuiropen 'https://i.redd.it/XxxXxxXXxxxX.png'
    $ tuiropen 'https://www.reddit.com/gallery/1xxXxx5'
    $ tuiropen 'https://v.redd.it/0xxxxxXXx9xx1'
    $ tuiropen 'https://i.redd.it/33xXXXxXxxXx1.gif'
    $ tuiropen ...
"""

from __future__ import annotations

import argparse
import logging
import os
import secrets
import string
import sys
import tempfile
from pathlib import Path

import sh
from RedDownloader import RedDownloader

__version__ = '0.0.2'
__appname__ = 'tuiropen'
TEMP = Path(tempfile.gettempdir()) / __appname__

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] [%(asctime)s] %(message)s',
)
logger = logging.getLogger(__name__)


def notify(mesg: str, icon: str = 'mpv') -> int:
    return sh.notify_send(
        f'--app-name={__appname__}',
        '--icon',
        icon,
        __appname__.upper(),
        mesg,
    )


def notify_open(url: str, filetype: str) -> int:
    t = 'video' if filetype == 'v' else 'image'
    return notify(f'opening {t} {url!s}', icon=t)


def play(file: str) -> int:
    p = sh.mpv(file, _bg=True)
    p.wait()
    return 0


def view(file: str) -> int:
    return sh.nsxiv(file, '-b')


def open_file(file: str, filetype: str) -> int:
    if filetype == 'g':
        return view(file)
    if filetype == 'i':
        return view(file + '.jpeg')
    if filetype == 'v':
        return play(file + '.mp4')
    if filetype == 'gif':
        return play(file + '.gif')

    logger.error(f'{file!r} is not supported')
    return 1


def setup_args() -> argparse.Namespace:
    parse = argparse.ArgumentParser(
        prog=__appname__, description='open URLs from tuir'
    )
    parse.add_argument('url', help='url to open')
    return parse.parse_args()


def ram_string(lenght: int = 12) -> str:
    return ''.join(secrets.choice(string.ascii_letters) for _ in range(lenght))


def main() -> int:
    args = setup_args()
    TEMP.mkdir(exist_ok=True)
    os.chdir(TEMP)
    filetmp = TEMP / ram_string()
    filename = filetmp.as_posix()

    try:
        file = RedDownloader.Download(
            url=args.url,
            verbose=True,
            output=filename,
        )
        filetype = file.GetMediaType()
        notify_open(args.url, filetype)
        open_file(filename, filetype)
    except AttributeError as exc:
        notify(f'<b>{exc}</b>', icon='dialog-error-symbolic')
        logger.error(exc)
    except KeyboardInterrupt as exc:
        logger.error(exc)

    return 0


if __name__ == '__main__':
    sys.exit(main())