import argparse
import logging
import socket
from typing import Tuple

import pandas as pd
import qrcode
from PIL import Image, ImageChops


def dashboard_qrcode(size: Tuple[int, int], port: int = 8000) -> Image.Image:
    """Generate a qrcode pointing to the dashboard url.

    Args:
        sie: the sie of the image, width and height.
        port: the port number on which the dashboard is hosted.

    Returns:
        The qrcode image.
    """
    min_dim = min(size)

    url = f"http://{socket.gethostname()}.local:{port}"
    qr = qrcode.make(url)
    qr = trim(qr)
    qr = qr.resize((min_dim, min_dim))
    base = Image.new("1", size, 1)
    base.paste(qr, (base.size[0] // 2 - qr.size[0] // 2, 0))
    return base


def trim(image: Image.Image) -> Image.Image:
    """Trim white space.

    See:
        https://stackoverflow.com/questions/10615901/trim-whitespace-using-pil

    Args:
        image: Image to trim.

    Returns:
        Trimmed image.
    """
    bg = Image.new(image.mode, image.size, image.getpixel((0, 0)))
    diff = ImageChops.difference(image, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        return image.crop(bbox)
    else:
        return image


class RawTextArgumentDefaultsHelpFormatter(
    argparse.RawTextHelpFormatter, argparse.ArgumentDefaultsHelpFormatter
):
    pass


def now() -> pd.Timestamp:
    """Return the current timestamp."""
    return pd.to_datetime("now", utc=True)


def set_verbosity(logger: logging.Logger, verbosity: int) -> logging.Logger:
    """Set the logger's verbosity.

    Args:
        logger: `logging.Logger`.
        verbosity: verbosity level, 1, or 2.

    Return:
        The `logging.Logger` object with configured verbosity.
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
