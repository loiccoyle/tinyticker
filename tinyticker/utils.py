import argparse
import json
import socket
from datetime import datetime, timezone
from urllib.request import urlopen

import qrcode
from packaging.version import Version
from PIL import Image, ImageChops


def dashboard_qrcode(epd_width: int, epd_height: int, port: int = 8000) -> Image.Image:
    """Generate a qrcode pointing to the dashboard url.

    Args:
        epd_width: the width of the ePaper display.
        epd_height: the height of the ePaper display.
        port: the port number on which the dashboard is hosted.

    Returns:
        The qrcode image.
    """
    url = f"http://{socket.gethostname()}.local:{port}"
    qr = qrcode.make(url)
    qr = trim(qr)
    qr = qr.resize((epd_width, epd_width))
    base = Image.new("1", (epd_height, epd_width), 1)
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


def check_for_update(current_version: str, **kwargs) -> bool:
    """Query the pypy index, returns True if an update is available.

    Args:
        current_version: the version string of the package.
        **kwargs: passed to `urllib.request.urlopen`.

    Returns:
        True if an update is available, False otherwise.
    """
    url = "https://pypi.python.org/pypi/{package}/json"
    response = json.loads(
        urlopen(url.format(package="tinyticker"), **kwargs).read().decode("utf8")
    )
    pypy_version = Version(response["info"]["version"])
    this_version = Version(current_version)
    return pypy_version > this_version


def now() -> datetime:
    """Return the current timestamp."""
    return datetime.now(timezone.utc)
