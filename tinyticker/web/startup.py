import logging
import subprocess
from pathlib import Path

LOGGER = logging.getLogger(__name__)
STARTUP_DIR = Path.home() / ".config" / "tinyticker" / "startup"


def run_scripts():
    scripts = STARTUP_DIR.glob("*")
    LOGGER.debug("Running startup scripts: %s", [file.name for file in scripts])
    processes = []
    for file in scripts:
        if file.is_file() and not file.name.startswith("."):
            LOGGER.debug("Running startup script: %s", file.name)
            processes.append(
                subprocess.Popen(
                    f"./{file}",
                    shell=True,
                )
            )
    return processes
