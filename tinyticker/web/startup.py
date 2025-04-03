import logging
import os
import subprocess
from pathlib import Path
from typing import List

LOGGER = logging.getLogger(__name__)
STARTUP_DIR = Path.home() / ".config" / "tinyticker" / "startup"


def get_scripts() -> List[Path]:
    """Get the startup scripts."""
    return [
        file
        for file in STARTUP_DIR.iterdir()
        if file.is_file() and not file.name.startswith(".") and os.access(file, os.X_OK)
    ]


def run_scripts(scripts: List[Path]) -> List[subprocess.Popen]:
    """Run the startup scripts. The scripts must be executable.

    Args:
        scripts: The scripts to run.

    Returns:
        The processes running the scripts.
    """
    processes = []
    for file in scripts:
        LOGGER.debug("Running startup script: %s", file.name)
        processes.append(subprocess.Popen(str(file), shell=True))
    return processes
