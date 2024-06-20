import argparse
import asyncio
import atexit
import os
import sys
from pathlib import Path
from typing import List

from watchdog.events import FileModifiedEvent, FileSystemEventHandler
from watchdog.observers import Observer

from . import __version__, logger
from .config import load_config_safe
from .display import Display
from .paths import CONFIG_FILE, PID_FILE
from .sequence import Sequence
from .utils import RawTextArgumentDefaultsHelpFormatter, set_verbosity
from .socket import run_server


def parse_args(args: List[str]) -> argparse.Namespace:
    """Parse the command line arguments."""
    parser = argparse.ArgumentParser(
        prog="tinyticker",
        description="""Raspberry Pi ticker using an ePaper display.

Note:
    Make sure SPI is enabled on your RPi and the BCM2835 driver is installed.
""",
        formatter_class=RawTextArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--config",
        help="Config file location.",
        type=Path,
        default=CONFIG_FILE,
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Verbosity.",
        action="count",
        default=0,
    )
    parser.add_argument(
        "--version",
        help="Show the version and exit.",
        action="version",
        version="%(prog)s {version}".format(version=__version__),
    )
    return parser.parse_args(args)


async def start_ticker(config_file: Path) -> None:
    """Start ticking.

    Args:
        config_file: config file path.
    """
    logger.info("Starting ticker task.")

    # Read config values
    tt_config = load_config_safe(config_file)

    display = Display.from_tinyticker_config(tt_config)
    sequence = Sequence.from_tinyticker_config(tt_config)
    logger.debug(sequence)

    # start the socket server to control the sequence.
    socket_server = asyncio.create_task(run_server(sequence))

    try:
        async for ticker, resp in sequence.start():
            logger.debug("Ticker response len(historical): %s", len(resp.historical))
            logger.debug("Ticker response current_price: %s", resp.current_price)
            display.show(ticker, resp)
    except Exception as exc:
        socket_server.cancel()
        logger.error(exc, stack_info=True)
        display.text(
            f"Whoops something broke:\n{exc}",
            show=True,
            weight="bold",
            fontsize="small",
        )
        await socket_server


async def run():
    args = parse_args(sys.argv[1:])
    config_file: Path = args.config

    if args.verbose > 0:
        set_verbosity(logger, args.verbose)
    logger.info("Tinyticker version: %s", __version__)

    # make sure the config file exists and can be parsed before setting up the file monitor
    load_config_safe(config_file)

    # write the process pid to file.
    pid = os.getpid()
    logger.info("PID file: %s", PID_FILE)
    logger.info("PID: %s", pid)
    if not PID_FILE.parent.is_dir():
        PID_FILE.parent.mkdir(parents=True, exist_ok=True)
    PID_FILE.write_text(str(pid))

    logger.debug("Args: %s", args)

    class ConfigModifiedHandler(FileSystemEventHandler):
        def on_modified(self, event):
            # when the file is modified, cancel the current task.
            logger.info(f"{event.src_path} was changed, cancelling ticker task.")
            if tick_task and not tick_task.done():
                tick_task.cancel()

    observer = Observer()
    config_modified_handler = ConfigModifiedHandler()
    observer.schedule(
        config_modified_handler, config_file, event_filter=[FileModifiedEvent]
    )
    observer.start()

    def cleanup():
        """Remove the PID file on exit."""
        logger.info("Exiting.")
        if PID_FILE.is_file():
            PID_FILE.unlink()
        observer.stop()
        observer.join()

    atexit.register(cleanup)

    # start ticking, we pass the config file so that is can be reloaded on refresh
    tick_task = None
    while True:
        if not tick_task or tick_task.done():
            try:
                tick_task = asyncio.create_task(start_ticker(config_file))
                await tick_task
            except asyncio.CancelledError:
                logger.info("Task cancelled.")


def main():
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        logger.info("Exiting.")
        sys.exit(0)


if __name__ == "__main__":
    main()
