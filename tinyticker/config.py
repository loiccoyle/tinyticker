import json
import logging
import subprocess
from pathlib import Path

from mplfinance._arg_validators import _get_valid_plot_types

from .settings import CONFIG_FILE, HOME_DIR, USER

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


def read(config_file: Path = CONFIG_FILE) -> dict:
    if config_file.is_file():
        LOGGER.debug("Reading config file.")
        with open(CONFIG_FILE, "r") as fd:
            return json.load(fd)
    else:
        LOGGER.debug("Fallback to default values.")
        return DEFAULT


def write(config: dict, config_file: Path = CONFIG_FILE) -> None:
    LOGGER.debug("Writing config file.")
    with open(config_file, "w") as fd:
        json.dump(config, fd, indent=2)


def write_default(config_file: Path = CONFIG_FILE) -> None:
    LOGGER.debug("Creating default.")
    if not config_file.parent.is_dir():
        config_file.mkdir(parents=True)
    write(DEFAULT)


SERVICE_FILE_DIR = Path("/etc/systemd/system/")
TINYTICKER_SERVICE = f"""[Unit]
Description=Raspberry Pi ticker on ePaper display.

[Service]
Type=simple
ExecStartPre=/usr/bin/nm-online
User={USER}
Group={USER}
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
User={USER}
Group={USER}
ExecStart=/usr/bin/sudo {HOME_DIR}/.local/bin/tinyticker-web -vv --port 80 --config-file {CONFIG_FILE}
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
                "systemctl daemon-reload",
                stderr=subprocess.STDOUT,
                shell=True,
            )
            output = subprocess.check_output(
                f"systemctl enable {service_file_name}",
                stderr=subprocess.STDOUT,
                shell=True,
            )
            LOGGER.info(output.decode("utf8"))
        except subprocess.CalledProcessError:
            LOGGER.error("Enabling service %s failed.", service_file_name)
            raise

    tinyticker_service_file = systemd_service_dir / "tinyticker.service"
    tinyticker_web_service_file = systemd_service_dir / "tinyticker-web.service"

    write_service(tinyticker_service_file, TINYTICKER_SERVICE)
    write_service(tinyticker_web_service_file, TINYTICKER_WEB_SERVICE)

    enable_service(tinyticker_service_file.name)
    enable_service(tinyticker_web_service_file.name)
