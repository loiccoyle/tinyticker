import argparse
import getpass
import logging
import os
from pathlib import Path
import socket

from PIL import Image, ImageChops
import qrcode

from .waveshare_lib.epd2in13_V2 import EPD_HEIGHT, EPD_WIDTH

USER = os.environ.get("SUDO_USER", getpass.getuser())
HOME_DIR = Path(os.path.expanduser(f"~{USER}"))

CONFIG_DIR = HOME_DIR / ".config" / "tinyticker"
CONFIG_FILE = CONFIG_DIR / "config.json"

TMP_DIR = Path("/tmp/tinyticker/")
if not TMP_DIR.is_dir():
    TMP_DIR.mkdir(parents=True)
PID_FILE = TMP_DIR / "tinyticker_pid"


class RawTextArgumentDefaultsHelpFormatter(
    argparse.RawTextHelpFormatter, argparse.ArgumentDefaultsHelpFormatter
):
    pass


def set_verbosity(logger: logging.Logger, verbosity: int) -> logging.Logger:
    """Set the verbosity.

    Args:
        logger: `logging.Logger`.
        verbosity: verbosity level, 1, or 2.

    Return:
        The same logger object.
    """
    verbose_map = {1: logging.INFO, 2: logging.DEBUG}
    level = verbose_map[verbosity]
    # from https://docs.python.org/3/howto/logging.html#configuring-logging
    logger.setLevel(level)
    # create console handler and set level to debug
    handler = logging.StreamHandler()
    handler.setLevel(level)
    # create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s: %(message)s", "%H:%M:%S"
    )
    # add formatter to handler
    handler.setFormatter(formatter)
    # add ch to logger
    logger.addHandler(handler)
    return logger


def generate_qrcode(port: int = 8000) -> Image.Image:
    url = f"https://{socket.gethostname()}.local:{port}"
    qr = qrcode.make(url)
    qr = trim(qr)
    qr = qr.resize((EPD_WIDTH, EPD_WIDTH))
    base = Image.new("1", (EPD_HEIGHT, EPD_WIDTH), 1)
    base.paste(qr, (base.size[0] // 2 - qr.size[0] // 2, 0))
    return base


def trim(im: Image.Image) -> Image.Image:
    """Trim white space."""
    bg = Image.new(im.mode, im.size, im.getpixel((0, 0)))  # type: ignore
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)
    else:
        return im
