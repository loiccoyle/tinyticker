import argparse
import json
from urllib.request import urlopen

from packaging.version import Version
from PIL import Image, ImageChops

from . import __version__


def trim(image: Image.Image) -> Image.Image:
    """Trim white space.

    Args:
        image: Image to trim.

    Returns:
        Trimmed image.
    """
    bg = Image.new(image.mode, image.size, image.getpixel((0, 0)))  # type: ignore
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


def check_for_update(**kwargs) -> bool:
    """Query the pypy index, returns True if an update is available.

    Args:
        **kwargs: passed to `urllib.request.urlopen`.

    Returns:
        True if an update is available, False otherwise.
    """
    url = "https://pypi.python.org/pypi/{package}/json"
    response = json.loads(
        urlopen(url.format(package="tinyticker"), **kwargs).read().decode("utf8")
    )
    pypy_version = Version(response["info"]["version"])
    current_version = Version(__version__)
    return pypy_version > current_version
