from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "tinyticker"
if not CONFIG_DIR.is_dir():
    CONFIG_DIR.mkdir(parents=True)
CONFIG_FILE = CONFIG_DIR / "config.json"
