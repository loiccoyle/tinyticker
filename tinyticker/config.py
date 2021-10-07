import json

from .settings import CONFIG_FILE

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
        with open(CONFIG_FILE, "r") as config_file:
            return json.load(config_file)
    else:
        return {}


def write(config: dict) -> None:
    with open(CONFIG_FILE, "w") as config_file:
        json.dump(config, config_file, indent=2)


# Write the default config
if not CONFIG_FILE.is_file():
    write(DEFAULT)
