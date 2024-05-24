import logging
import subprocess
from pathlib import Path

LOGGER = logging.getLogger(__name__)
STARTUP_DIR = Path.home() / ".config" / "tinyticker" / "startup"


def run_scripts():
    files = STARTUP_DIR.glob("*")
    LOGGER.debug("Running startup scripts: %s", [file.name for file in files])
    return [
        subprocess.Popen(
            f"./{file}",
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        for file in files
    ]
