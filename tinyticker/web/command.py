import logging
import os
import signal
import subprocess
from typing import Callable, List

from ..settings import PID_FILE

LOGGER = logging.getLogger(__name__)


COMMANDS = {}


def register(func: Callable) -> Callable:
    COMMANDS[func.__name__.replace("_", " ")] = func
    return func


def try_command(command: List[str]) -> None:
    """Try to run a command.

    Args:
        command: shell command.
    """
    try:
        output = subprocess.check_output(
            command,
            shell=True,
            stderr=subprocess.STDOUT,
        )
        if output:
            LOGGER.info(output)
    except subprocess.CalledProcessError as exc:
        LOGGER.error("Command failed.")
        LOGGER.error(exc.output)


@register
def restart():
    """Restart the tinyticker process, using the SIGUSR1 signal."""
    if PID_FILE.is_file():
        LOGGER.info("Seding SIGUSR1 to tinyticker.")
        with open(PID_FILE, "r") as pid_file:
            pid = int(pid_file.readline())
        os.kill(pid, signal.SIGUSR1)
    else:
        LOGGER.info("tinyticker is not runnning.")


@register
def reboot():
    """Reboot the Raspberry Pi, requires sudo."""
    LOGGER.info("Rebooting.")
    try_command(["sudo", "shutdown", "-h", "now"])


@register
def wifi_reset():
    """Reset the Raspberry Pi's comitup settings, requires sudo."""
    LOGGER.info("Removing comitup connection config.")
    try_command(["sudo", "comitup-cli", "d"])


@register
def update():
    """Update tinyticker."""
    LOGGER.info("Updating tinyticker.")
    try_command(["pipx", "upgrade", "tinyticker"])
