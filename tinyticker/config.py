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


SERVICE_FILE_DIR = Path("/etc/systemd/system/")
TINYTICKER_SERVICE = f"""[Unit]
Description=Raspberry Pi ticker on ePaper display.
After=networking.service

[Service]
Type=simple
ExecStartPre={HOME_DIR}/.local/bin/tinyticker-web --port 80 --show-qrcode
ExecStart={HOME_DIR}/.local/bin/tinyticker --config {CONFIG_FILE} -vv
Restart=on-failure
RestartSec=30s
StandardOutput=file:/tmp/tinyticker1.log
StandardError=file:/tmp/tinyticker2.log

[Install]
WantedBy=multi-user.target"""

# the user and group lines are required to be able to run the update command
TINYTICKER_WEB_SERVICE = f"""[Unit]
Description=Raspberry Pi ticker on epaper display, web interface.
After=networking.service

[Service]
Type=simple
User={USER}
Group={USER}
ExecStart=sh -c '! type comitup-cli || /usr/bin/sudo comitup-cli i | grep -q "CONNECTED" && /usr/bin/sudo {HOME_DIR}/.local/bin/tinyticker-web --port 80 --config {CONFIG_FILE} -vv'
Restart=on-failure
RestartSec=5s
StandardOutput=file:/tmp/tinyticker-web1.log
StandardError=file:/tmp/tinyticker-web2.log

[Install]
WantedBy=multi-user.target"""


def start_on_boot(systemd_service_dir: Path = SERVICE_FILE_DIR) -> None:
    """Create and enable the systemd service. Requires sudo.

    Args:
        systemd_service_dir: folder location in which to place the unit file.
    """

    def write_unit(unit_file: Path, content: str) -> None:
        """Helper function to write the service file.

        Args:
            unit_file: unit file destination.
            content: content to write into the unit file.
        """
        if unit_file.is_file():
            LOGGER.warning("%s already exists, overwriting.", str(unit_file))
        unit_file.write_text(content)

    def enable_service(unit_name: str) -> None:
        """Enable a systemd service.

        Args:
            unit_name: the name of the systemd unit.
        """
        try:
            subprocess.check_output(
                "systemctl daemon-reload",
                stderr=subprocess.STDOUT,
                shell=True,
            )
            output = subprocess.check_output(
                f"systemctl enable {unit_name}",
                stderr=subprocess.STDOUT,
                shell=True,
            )
            if output:
                LOGGER.info(output.decode("utf8"))
        except subprocess.CalledProcessError:
            LOGGER.error("Enabling service %s failed.", unit_name)
            raise

    tinyticker_service_file = systemd_service_dir / "tinyticker.service"
    tinyticker_web_service_file = systemd_service_dir / "tinyticker-web.service"

    write_unit(tinyticker_service_file, TINYTICKER_SERVICE)
    write_unit(tinyticker_web_service_file, TINYTICKER_WEB_SERVICE)

    enable_service(tinyticker_service_file.name)
    enable_service(tinyticker_web_service_file.name)
