import json

from .settings import CONFIG_FILE


def read() -> dict:
    with open(CONFIG_FILE, "r") as config_file:
        return json.load(config_file)


def write(config: dict) -> None:
    with open(CONFIG_FILE, "w") as config_file:
        json.dump(config, config_file, indent=2)
