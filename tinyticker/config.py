import json
import logging

from .settings import CONFIG_FILE

LOGGER = logging.getLogger(__name__)

DEFAULT = {
    "api_key": None,
    "coin": "BTC",
    "currency": "USD",
    "interval": "hour",
    "lookback": None,
    "wait_time": None,
    "flip": False,
}


def read() -> dict:
    if CONFIG_FILE.is_file():
        LOGGER.debug("Reading config file.")
        with open(CONFIG_FILE, "r") as config_file:
            return json.load(config_file)
    else:
        LOGGER.debug("Fallback to default values.")
        return DEFAULT


def write(config: dict) -> None:
    LOGGER.debug("Writing config file.")
    with open(CONFIG_FILE, "w") as config_file:
        json.dump(config, config_file, indent=2)


# Write the default config
if not CONFIG_FILE.is_file():
    LOGGER.debug("No config file, creating default.")
    write(DEFAULT)
