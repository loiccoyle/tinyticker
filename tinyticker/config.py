import json
import logging

from mplfinance._arg_validators import _get_valid_plot_types

from .settings import CONFIG_FILE
from .ticker import INTERVAL_LOOKBACKS

LOGGER = logging.getLogger(__name__)

# remove hollow types because white on white doesn't show
TYPES = [
    plot_type for plot_type in _get_valid_plot_types() if "hollow" not in plot_type
]

DEFAULT = {
    "symbol_type": "stock",
    "api_key": None,
    "symbol": "AAPL",
    "currency": "USD",
    "interval": "5m",
    "lookback": INTERVAL_LOOKBACKS["5m"],
    "wait_time": None,
    "flip": False,
    "type": "candle",
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
