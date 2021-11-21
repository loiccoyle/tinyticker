import getpass
import logging
import os
import socket
import subprocess
from pathlib import Path

import qrcode
from PIL import Image

from .utils import trim

LOGGER = logging.getLogger(__name__)

USER = os.environ.get("SUDO_USER", getpass.getuser())
HOME_DIR = Path(os.path.expanduser(f"~{USER}"))

CONFIG_DIR = HOME_DIR / ".config" / "tinyticker"
CONFIG_FILE = CONFIG_DIR / "config.json"

TMP_DIR = Path("/tmp/tinyticker/")
LOG_DIR = Path("/var/log")
PID_FILE = TMP_DIR / "tinyticker_pid"


SERVICE_FILE_DIR = Path("/etc/systemd/system/")
TINYTICKER_SERVICE = f"""[Unit]
Description=Raspberry Pi ticker on ePaper display.
After=networking.service
After=tinyticker-qrcode.service

[Service]
Type=simple
ExecStart={HOME_DIR}/.local/bin/tinyticker --config {CONFIG_FILE} -vv
Restart=on-failure
RestartSec=30s
StandardOutput=file:{LOG_DIR}/tinyticker1.log
StandardError=file:{LOG_DIR}/tinyticker2.log

[Install]
WantedBy=multi-user.target"""

TINYTICKER_QR_SERVICE = f"""[Unit]
Description=Raspberry Pi ticker on ePaper display, qrcode.
After=networking.service

[Service]
Type=oneshot
ExecStart={HOME_DIR}/.local/bin/tinyticker-web --port 80 --show-qrcode --config {CONFIG_FILE}
Restart=on-failure
RestartSec=30s
StandardOutput=file:{LOG_DIR}/tinyticker-qrcode1.log
StandardError=file:{LOG_DIR}/tinyticker-qrcode2.log

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
StandardOutput=file:{LOG_DIR}/tinyticker-web1.log
StandardError=file:{LOG_DIR}/tinyticker-web2.log

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

    for unit_file, contents in zip(
        [
            systemd_service_dir / "tinyticker.service",
            systemd_service_dir / "tinyticker-web.service",
            systemd_service_dir / "tinyticker-qrcode.service",
        ],
        [
            TINYTICKER_SERVICE,
            TINYTICKER_WEB_SERVICE,
            TINYTICKER_QR_SERVICE,
        ],
    ):
        write_unit(unit_file, contents)
        enable_service(unit_file.name)


def set_verbosity(logger: logging.Logger, verbosity: int) -> logging.Logger:
    """Set the verbosity.

    Args:
        logger: `logging.Logger`.
        verbosity: verbosity level, 1, or 2.

    Return:
        The same logger object.
    """
    verbose_map = {1: logging.INFO, 2: logging.DEBUG}
    level = verbose_map[verbosity]
    # from https://docs.python.org/3/howto/logging.html#configuring-logging
    logger.setLevel(level)
    # create console handler and set level to debug
    handler = logging.StreamHandler()
    handler.setLevel(level)
    # create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s: %(message)s", "%H:%M:%S"
    )
    # add formatter to handler
    handler.setFormatter(formatter)
    # add ch to logger
    logger.addHandler(handler)
    return logger


def generate_qrcode(epd_width: int, epd_height: int, port: int = 8000) -> Image.Image:
    """Generate a qrcode pointing to the dashboard url.

    Args:
        port: the port number on which the dashboard is hosted.

    Returns:
        The qrcode image.
    """
    url = f"http://{socket.gethostname()}.local:{port}"
    qr = qrcode.make(url)
    qr = trim(qr)  # type: ignore
    qr = qr.resize((epd_width, epd_width))
    base = Image.new("1", (epd_height, epd_width), 1)
    base.paste(qr, (base.size[0] // 2 - qr.size[0] // 2, 0))
    return base
