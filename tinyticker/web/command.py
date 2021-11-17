import logging
import os
import signal
import subprocess
from typing import Callable, List, Union

from ..settings import PID_FILE, USER

LOGGER = logging.getLogger(__name__)
COMMANDS = {}


def register(func: Callable) -> Callable:
    """Register a function to appear in the commands section of the web interface."""
    COMMANDS[func.__name__.replace("_", " ")] = func
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
    """Restart the tinyticker process, using the SIGUSR1 signal."""
    if PID_FILE.is_file():
        LOGGER.info("Sending SIGUSR1 to tinyticker.")
        with open(PID_FILE, "r") as pid_file:
            pid = int(pid_file.readline())
        os.kill(pid, signal.SIGUSR1)
    else:
        LOGGER.info("tinyticker is not runnning.")


@register
def reboot() -> None:
    """Reboot the Raspberry Pi, requires sudo."""
    LOGGER.info("Rebooting.")
    try_command("sudo reboot")


@register
def wifi_reset() -> None:
    """Reset the Raspberry Pi's comitup settings, requires sudo."""
    LOGGER.info("Removing comitup connection config.")
    try_command("sudo comitup-cli d")
    reboot()


@register
def update() -> None:
    """Update tinyticker."""
    LOGGER.info("Updating tinyticker.")
    try_command(
        f"sudo -i -u {USER} -- sh -c \"type pipx > /dev/null && pipx upgrade tinyticker || pip install --upgrade tinyticker\""
    )
