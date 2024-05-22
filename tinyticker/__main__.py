import argparse
import atexit
import multiprocessing
import os
import signal
import sys
from pathlib import Path
from time import sleep
from typing import List

from watchdog.events import FileModifiedEvent, FileSystemEventHandler
from watchdog.observers import Observer

from . import __version__, logger
from .config import load_config_safe
from .display import Display
from .paths import CONFIG_FILE, PID_FILE
from .sequence import Sequence
from .tickers._base import TickerBase, TickerResponse
from .utils import RawTextArgumentDefaultsHelpFormatter, set_verbosity


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


def start_ticker_process(config_file: Path) -> multiprocessing.Process:
    """Create and start the ticker process.

    Args:
        config_file: config file path.

    Returns:
        The ticker process.
    """
    tick_process = multiprocessing.Process(target=start_ticker, args=(config_file,))
    tick_process.start()
    return tick_process


def show_ticker(ticker: TickerBase, resp: TickerResponse, display: Display):
    delta_range_start = resp.historical.iloc[0]["Open"]
    delta_range = 100 * (resp.current_price - delta_range_start) / delta_range_start

    top_string = f"{ticker.config.symbol}: $ {resp.current_price:.2f}"
    if ticker.config.avg_buy_price is not None:
        # calculate the delta from the average buy price
        delta_abp = (
            100
            * (resp.current_price - ticker.config.avg_buy_price)
            / ticker.config.avg_buy_price
        )
        top_string += f" {delta_abp:+.2f}%"

    xlim = None
    # if incomplete data, leave space for the missing data
    if len(resp.historical) < ticker.lookback:
        # the floats are to leave padding left and right of the edge candles
        xlim = (-0.75, ticker.lookback - 0.25)
    logger.debug("xlim: %s", xlim)
    display.plot(
        resp.historical,
        top_string=top_string,
        sub_string=f"{len(resp.historical)}x{ticker.config.interval} {delta_range:+.2f}%",
        show=True,
        xlim=xlim,
        type=ticker.config.plot_type,
        mav=ticker.config.mav,
        volume=ticker.config.volume,
    )


def start_ticker(config_file: Path) -> None:
    """Start ticking.

    Args:
        config_file: config file path.
    """
    logger.info("Starting ticker process")
    # Read config values
    tt_config = load_config_safe(config_file)

    display = Display.from_tinyticker_config(tt_config)
    sequence = Sequence.from_tinyticker_config(tt_config)
    logger.debug(sequence)

    try:
        for ticker, resp in sequence.start():
            logger.debug("API len(historical): %s", len(resp.historical))
            logger.debug("API current_price: %s", resp.current_price)
            show_ticker(ticker, resp, display)
    except Exception as exc:
        logger.error(exc, stack_info=True)
        display.text(
            f"Whoops something broke:\n{exc}",
            show=True,
            weight="bold",
            fontsize="small",
        )


def main():
    args = parse_args(sys.argv[1:])
    config_file: Path = args.config

    if args.verbose > 0:
        set_verbosity(logger, args.verbose)
    logger.info("Tinyticker version: %s", __version__)

    # make sure the config file exists and can be parsed before setting up the file
    # monitor
    load_config_safe(config_file)

    # write the process pid to file.
    pid = os.getpid()
    logger.info("PID file: %s", PID_FILE)
    logger.info("PID: %s", pid)
    if not PID_FILE.parent.is_dir():
        PID_FILE.parent.mkdir(parents=True, exist_ok=True)
    PID_FILE.write_text(str(pid))

    logger.debug("Args: %s", args)

    def refresh(*_) -> None:
        """Kill the ticker process, it gets restarted in the main thread."""
        logger.info("Refreshing ticker process.")
        if not tick_process._closed and tick_process.is_alive():  # type: ignore
            tick_process.kill()
            tick_process.join()
            tick_process.close()

    class ConfigModifiedHandler(FileSystemEventHandler):
        def on_modified(self, event):
            logger.info(f"{event.src_path} was changed, refreshing ticker thread.")
            refresh()

    observer = Observer()
    config_modified_handler = ConfigModifiedHandler()
    observer.schedule(
        config_modified_handler, config_file, event_filter=[FileModifiedEvent]
    )
    observer.start()

    signal.signal(signal.SIGUSR2, refresh)

    def cleanup():
        """Remove the PID file on exit."""
        logger.info("Exiting.")
        if PID_FILE.is_file():
            PID_FILE.unlink()
        observer.stop()
        observer.join()
        tick_process.kill()
        tick_process.join()

    atexit.register(cleanup)

    # start ticking
    tick_process = start_ticker_process(config_file)
    while True:
        if tick_process._closed or not tick_process.is_alive():  # type: ignore
            tick_process = start_ticker_process(config_file)
        else:
            sleep(1)


if __name__ == "__main__":
    main()
