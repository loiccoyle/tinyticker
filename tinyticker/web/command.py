import logging
import os
import signal
import subprocess
from typing import Callable

from ..settings import PID_FILE

LOGGER = logging.getLogger(__name__)


COMMANDS = {}


def register(func: Callable) -> Callable:
    COMMANDS[func.__name__] = func
    return func


@register
def restart():
    """Kill the tinyticker process. Systemd is left to restart it."""
    if PID_FILE.is_file():
        LOGGER.info("Killing tinyticker.")
        with open(PID_FILE, "r") as pid_file:
            pid = int(pid_file.readline())
        os.kill(pid, signal.SIGKILL)
    else:
        LOGGER.info("tinyticker is not runnning.")


@register
def reboot():
    """Reboot the Raspberry Pi, requires sudo."""
    LOGGER.info("Rebooting.")
    subprocess.Popen(["sudo", "shutdown", "-h", "now"])
