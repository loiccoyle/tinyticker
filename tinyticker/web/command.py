import logging
import os
import signal
import subprocess

from ..settings import PID_FILE

LOGGER = logging.getLogger(__name__)


def restart():
    if PID_FILE.is_file():
        LOGGER.info("Killing tinyticker.")
        with open(PID_FILE, "r") as pid_file:
            pid = int(pid_file.readline())
        os.kill(pid, signal.SIGKILL)
    else:
        LOGGER.info("tinyticker is not runnning.")


def reboot():
    LOGGER.info("Rebooting.")
    subprocess.Popen(["sudo", "shutdown", "-h", "now"])


COMMANDS = dict(restart=restart, reboot=reboot)
