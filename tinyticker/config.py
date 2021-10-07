import json

from .settings import CONFIG_FILE


def read() -> dict:
    if CONFIG_FILE.is_file():
        with open(CONFIG_FILE, "r") as config_file:
            return json.load(config_file)
    else:
        return {}


def write(config: dict) -> None:
    with open(CONFIG_FILE, "w") as config_file:
        json.dump(config, config_file, indent=2)
