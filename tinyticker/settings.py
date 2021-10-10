import argparse
import getpass
import logging
import os
from pathlib import Path

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
