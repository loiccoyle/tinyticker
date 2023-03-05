import getpass
import os
from pathlib import Path

USER = os.environ.get("SUDO_USER", getpass.getuser())
HOME_DIR = Path(os.path.expanduser(f"~{USER}"))

CONFIG_DIR = HOME_DIR / ".config" / "tinyticker"
CONFIG_FILE = CONFIG_DIR / "config.json"

TMP_DIR = Path("/tmp/tinyticker/")
LOG_DIR = Path("/var/log")
PID_FILE = TMP_DIR / "tinyticker_pid"
