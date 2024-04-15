import dataclasses as dc
import logging
import os
import signal
import subprocess
from typing import Callable, Dict, List, Optional, Union

from pip._internal.cli.main import main as pipmain

from ..config import TinytickerConfig
from ..paths import CONFIG_FILE, PID_FILE

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
    """Restart the tinyticker process."""
    if PID_FILE.is_file():
        LOGGER.info("Sending SIGUSR1 to tinyticker.")
        with open(PID_FILE, "r") as pid_file:
            pid = int(pid_file.readline())
        os.kill(pid, signal.SIGUSR1)
    else:
        LOGGER.info("tinyticker is not runnning.")


@register
def refresh() -> None:
    """Refresh tinyticker's ticker process."""
    if PID_FILE.is_file():
        LOGGER.info("Sending SIGUSR2 to tinyticker.")
        with open(PID_FILE, "r") as pid_file:
            pid = int(pid_file.readline())
        os.kill(pid, signal.SIGUSR2)
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
    args = ["install", "--upgrade", "tinyticker"]
    # rpi requires an added flag to update system packages
    # https://www.raspberrypi.com/documentation/computers/os.html#about-python-virtual-environments
    error = pipmain(args + ["--break-system-packages"])
    if error:
        # if for some reason we are not running on an rpi, try again without the flag
        error = pipmain(args)


@register
def default() -> None:
    """Write the default config."""
    LOGGER.info("Setting config to default.")
    TinytickerConfig().to_file(CONFIG_FILE)
    refresh()
