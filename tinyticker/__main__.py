import argparse
import atexit
import multiprocessing
import os
import signal
import sys
from pathlib import Path
from time import sleep
from typing import List

from . import __version__, logger
from .config import TinytickerConfig
from .display import Display
from .paths import CONFIG_FILE, PID_FILE
from .ticker import Sequence
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


def start_ticker(config_file: Path) -> None:
    """Start ticking.

    Args:
        config_file: config file path.
    """
    logger.info("Starting ticker process")
    # Read config values
    tt_config = TinytickerConfig.from_file(config_file)

    display = Display.from_tinyticker_config(tt_config)
    sequence = Sequence.from_tinyticker_config(tt_config)
    logger.debug(sequence)

    for ticker, resp in sequence.start():
        try:
            if resp.historical is None or resp.historical.empty:
                logger.debug("response data empty.")
                display.text(
                    f"No data for {ticker.symbol} in lookback range: {ticker.lookback}x{ticker.interval}",
                    show=True,
                    weight="bold",
                )
            else:
                logger.debug("API len(historical): %s", len(resp.historical))
                logger.debug("API current_price: %s", resp.current_price)
                delta = (
                    100
                    * (resp.current_price - resp.historical.iloc[0]["Open"])
                    / resp.historical.iloc[0]["Open"]
                )
                xlim = None
                # if incomplete data, leave space for the missing data
                if len(resp.historical) < ticker.lookback:
                    # the floats are to leave padding left and right of the edge candles
                    xlim = (-0.75, ticker.lookback - 0.25)
                logger.debug("xlim: %s", xlim)
                display.plot(
                    resp.historical,
                    resp.current_price,
                    top_string=f"{ticker.symbol}: $",
                    sub_string=f"{len(resp.historical)}x{ticker.interval}",
                    delta=delta,
                    show=True,
                    xlim=xlim,
                    type=ticker._display_kwargs.pop("plot_type", "candle"),
                    **ticker._display_kwargs,
                )
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

    # if the config file is not present, write the default values
    if not config_file.is_file():
        config_file.parent.mkdir(parents=True)
        # write defaults to file
        TinytickerConfig().to_file(config_file)

    # write the process pid to file.
    pid = os.getpid()
    logger.info("PID file: %s", PID_FILE)
    logger.info("PID: %s", pid)
    if not PID_FILE.parent.is_dir():
        PID_FILE.parent.mkdir(parents=True, exist_ok=True)
    PID_FILE.write_text(str(pid))

    logger.debug("Args: %s", args)

    #  setup signal handlers
    def restart(*_) -> None:
        """Restart both the ticker and the main thread."""
        logger.info("Restarting.")
        os.execv(sys.argv[0], sys.argv)

    signal.signal(signal.SIGUSR1, restart)

    def refresh(*_) -> None:
        """Kill the ticker process, it gets restarted in the main thread."""
        logger.info("Refreshing ticker process.")
        tick_process.kill()
        tick_process.join()
        tick_process.close()

    signal.signal(signal.SIGUSR2, refresh)

    def cleanup():
        """Remove the PID file on exit."""
        logger.info("Exiting.")
        if PID_FILE.is_file():
            PID_FILE.unlink()

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
