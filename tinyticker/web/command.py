import dataclasses as dc
import logging
import subprocess
from typing import Callable, Dict, List, Optional, Union

from pip._internal.cli.main import main as pipmain

from ..config import TinytickerConfig
from ..paths import CONFIG_FILE, PID_FILE
from ..socket import send_message, Message, SOCKET_FILE

LOGGER = logging.getLogger(__name__)
COMMANDS: Dict[str, "Command"] = {}


@dc.dataclass
class Command:
    func: Callable[[None], None]
    name: str
    desc: Optional[str]


def register(func: Callable) -> Callable:
    """Register a function to appear in the commands section of the web interface."""
    cmd = Command(func, func.__name__.replace("_", " "), func.__doc__)
    COMMANDS[cmd.name] = cmd
    return func


def try_command(command: Union[List[str], str]) -> None:
    """Try to run a command.

    Args:
        command: shell command.
    """
    try:
        LOGGER.info("Running command: %s", command)
        output = subprocess.check_output(
            command,
            shell=True,
            stderr=subprocess.STDOUT,
        )
        if output:
            LOGGER.info(output.decode("utf8"))
    except subprocess.CalledProcessError as exc:
        LOGGER.error("Command failed.")
        LOGGER.error(exc.output.decode("utf8"))


@register
def restart() -> None:
    """Restart the tinyticker and tinyticker-web systemd services."""
    LOGGER.info("Restarting services.")
    try_command("systemctl --user restart tinyticker")
    try_command("systemctl --user restart tinyticker-web")


@register
def next_ticker() -> None:
    """Skip the current ticker and display the next one."""
    if PID_FILE.is_file() and SOCKET_FILE.is_socket():
        LOGGER.info("Sending '%s' to tinyticker socket.", Message.NEXT.value)
        send_message(Message.NEXT)
    else:
        LOGGER.info("tinyticker is not runnning.")


@register
def previous_ticker() -> None:
    """Skip the current ticker and display the previous one."""
    if PID_FILE.is_file() and SOCKET_FILE.is_socket():
        LOGGER.info("Sending '%s' to tinyticker.", Message.PREVIOUS.value)
        send_message(Message.PREVIOUS)
    else:
        LOGGER.info("tinyticker is not runnning.")


@register
def refresh() -> None:
    """Refresh tinyticker's ticker process."""
    if PID_FILE.is_file():
        LOGGER.info("Touching config file.")
        CONFIG_FILE.touch()
    else:
        LOGGER.info("tinyticker is not runnning.")


@register
def reboot() -> None:
    """Reboot the  RPi, requires sudo."""
    LOGGER.info("Rebooting.")
    try_command("sudo reboot")


@register
def wifi_reset() -> None:
    """Reset the RPi's comitup settings, requires sudo."""
    LOGGER.info("Removing comitup connection config.")
    try_command("sudo comitup-cli d")
    reboot()


@register
def update() -> None:
    """Update tinyticker with pip."""
    # the `--break-system-packages` flag is required to update system packages on rpi
    # https://www.raspberrypi.com/documentation/computers/os.html#about-python-virtual-environments
    # it should be safe as we are installing in the user pkgs and this user is solely dedicated
    # to running tinyticker
    args = ["install", "--user", "--upgrade", "tinyticker", "--break-system-packages"]
    LOGGER.info(f"Updating tinyticker with: pip {' '.join(args)}")
    error = pipmain(args)
    if not error:
        LOGGER.info("Update successful, restarting the services.")
        restart()


@register
def default() -> None:
    """Write the default config."""
    LOGGER.info("Setting config to default.")
    TinytickerConfig().to_file(CONFIG_FILE)
    refresh()
