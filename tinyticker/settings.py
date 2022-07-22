import getpass
import logging
import os
import socket
from pathlib import Path

import qrcode
from PIL import Image

from .utils import trim

LOGGER = logging.getLogger(__name__)

USER = os.environ.get("SUDO_USER", getpass.getuser())
HOME_DIR = Path(os.path.expanduser(f"~{USER}"))

CONFIG_DIR = HOME_DIR / ".config" / "tinyticker"
CONFIG_FILE = CONFIG_DIR / "config.json"

TMP_DIR = Path("/tmp/tinyticker/")
LOG_DIR = Path("/var/log")
PID_FILE = TMP_DIR / "tinyticker_pid"


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


def generate_qrcode(epd_width: int, epd_height: int, port: int = 8000) -> Image.Image:
    """Generate a qrcode pointing to the dashboard url.

    Args:
        port: the port number on which the dashboard is hosted.

    Returns:
        The qrcode image.
    """
    url = f"http://{socket.gethostname()}.local:{port}"
    qr = qrcode.make(url)
    qr = trim(qr)  # type: ignore
    qr = qr.resize((epd_width, epd_width))
    base = Image.new("1", (epd_height, epd_width), 1)
    base.paste(qr, (base.size[0] // 2 - qr.size[0] // 2, 0))
    return base
