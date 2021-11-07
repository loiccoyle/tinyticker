import json
import logging
from pathlib import Path

from .settings import CONFIG_FILE

LOGGER = logging.getLogger(__name__)

# remove hollow types because white on white doesn't show
TYPES = ["candlestick", "line", "ohlc"]
DEFAULT = {
    "epd_model": "EPD_v2",
    "symbol_type": "stock",
    "api_key": None,
    "symbol": "AAPL",
    "interval": "5m",
    "lookback": None,
    "wait_time": None,
    "flip": False,
    "type": "candlestick",
    "mav": None,
}


def read(config_file: Path = CONFIG_FILE) -> dict:
    """Read the config file and return a dictionary.

    Args:
        config_file: path of the config file.
    """
    if config_file.is_file():
        LOGGER.debug("Reading config file: %s", config_file)
        with open(config_file, "r") as fd:
            return json.load(fd)
    else:
        LOGGER.debug("Fallback to default values.")
        return DEFAULT


def write(config: dict, config_file: Path = CONFIG_FILE) -> None:
    """Write the config file.

    Args:
        config: dictionary containing the contents of the config.
        config_file: path of the config file.
    """
    config_dir = config_file.parent
    if not config_dir.is_dir():
        LOGGER.debug("Creating config dir: %s", config_dir)
        config_dir.mkdir(parents=True)

    LOGGER.debug("Writing config file: %s", config_file)
    with open(config_file, "w") as fd:
        json.dump(config, fd, indent=2)


def write_default(config_file: Path = CONFIG_FILE) -> None:
    """Write the default values to the config file.

    Args:
        config_file: path of the config file.
    """
    LOGGER.debug("Creating default config: %s", config_file)
    if not config_file.parent.is_dir():
        config_file.parent.mkdir(parents=True)
    write(DEFAULT, config_file)
