import getpass
import json
import logging
import os
import subprocess
from pathlib import Path

from mplfinance._arg_validators import _get_valid_plot_types

from .settings import CONFIG_FILE

LOGGER = logging.getLogger(__name__)

# remove hollow types because white on white doesn't show
TYPES = ["candlestick", "line", "ohlc"]
DEFAULT = {
    "symbol_type": "stock",
    "api_key": None,
    "symbol": "AAPL",
    "interval": "5m",
    "lookback": None,
    "wait_time": None,
    "flip": False,
    "type": "candlestick",
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

USER = os.environ.get("SUDO_USER", getpass.getuser())
HOME_DIR = os.path.expanduser(f"~{USER}")
SERVICE_FILE_DIR = Path("/etc/systemd/system/")
TINYTICKER_SERVICE = f"""[Unit]
Description=Raspberry Pi ticker on ePaper display.

[Service]
Type=simple
ExecStartPre=/usr/bin/nm-online
ExecStart={HOME_DIR}/.local/bin/tinyticker --config -vv
Restart=on-failure
RestartSec=30s
StandardOutput=file:/tmp/tinyticker1.log
StandardError=file:/tmp/tinyticker2.log

[Install]
WantedBy=multi-user.target"""

TINYTICKER_WEB_SERVICE = f"""[Unit]
Description=Raspberry Pi ticker on epaper display, web interface.

[Service]
Type=simple
ExecStartPre=/usr/bin/nm-online
ExecStart={HOME_DIR}/.local/bin/tinyticker-web -vv --port 80
Restart=on-failure
RestartSec=30s
StandardOutput=file:/tmp/tinyticker-web1.log
StandardError=file:/tmp/tinyticker-web2.log

[Install]
WantedBy=multi-user.target"""


def start_on_boot(systemd_service_dir: Path = SERVICE_FILE_DIR) -> None:
    """Create and enable the systemd service. Requires sudo."""

    def write_service(service_file: Path, content: str) -> None:
        """Helper function to write the service file."""
        if service_file.is_file():
            LOGGER.warning("%s already exists, overwriting.", str(service_file))
        service_file.write_text(content)

    def enable_service(service_file_name: str) -> None:
        try:
            subprocess.check_output(
                ["sudo", "systemctl", "daemon-reload"],
                stderr=subprocess.STDOUT,
                shell=True,
            )
            subprocess.check_output(
                ["sudo", "systemctl", "enable", service_file_name],
                stderr=subprocess.STDOUT,
                shell=True,
            )
        except subprocess.CalledProcessError:
            LOGGER.error("Enabling service %s failed.", service_file_name)
            raise

    tinyticker_service_file = systemd_service_dir / "tinyticker.service"
    tinyticker_web_service_file = systemd_service_dir / "tinyticker-web.service"

    write_service(tinyticker_service_file, TINYTICKER_SERVICE)
    write_service(tinyticker_web_service_file, TINYTICKER_WEB_SERVICE)

    enable_service(tinyticker_service_file.name)
    enable_service(tinyticker_web_service_file.name)
