import argparse
import atexit
import multiprocessing
import os
import signal
import sys
from pathlib import Path
from time import sleep
from typing import Any, Dict, List

from . import __version__, config, logger
from .config import DEFAULT, TYPES
from .display import Display
from .settings import CONFIG_FILE, PID_FILE, set_verbosity
from .ticker import INTERVAL_LOOKBACKS, SYMBOL_TYPES, Sequence, Ticker
from .utils import RawTextArgumentDefaultsHelpFormatter
from .waveshare_lib.models import MODELS


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
    # parser.add_argument(
    #     "--epd-model",
    #     help="ePaper display model.",
    #     type=str,
    #     default="EPD_v2",
    #     choices=MODELS.keys(),
    # )
    # parser.add_argument(
    #     "-a",
    #     "--api-key",
    #     help="CryptoCompare API key, https://min-api.cryptocompare.com/pricing.",
    #     type=str,
    #     default=DEFAULT["api_key"],
    # )
    # parser.add_argument(
    #     "--symbol-type",
    #     help="The type of the symbol.",
    #     type=str,
    #     choices=SYMBOL_TYPES,
    #     default=DEFAULT["tickers"][0]["stock"],
    # )
    # parser.add_argument(
    #     "-s",
    #     "--symbol",
    #     help="Asset symbol.",
    #     type=str,
    #     default=DEFAULT["tickers"][0]["symbol"],
    # )
    # parser.add_argument(
    #     "-i",
    #     "--interval",
    #     help="Interval.",
    #     type=str,
    #     choices=INTERVAL_LOOKBACKS.keys(),
    #     default=DEFAULT["tickers"][0]["interval"],
    # )
    # parser.add_argument(
    #     "-l",
    #     "--lookback",
    #     help="Look back amount.",
    #     type=int,
    #     default=DEFAULT["tickers"][0]["lookback"],
    # )
    # parser.add_argument(
    #     "-w",
    #     "--wait-time",
    #     help="Wait time in seconds.",
    #     type=int,
    #     default=DEFAULT["tickers"][0]["wait_time"],
    # )
    # parser.add_argument(
    #     "-t",
    #     "--type",
    #     help="Plot style, see mplfinance.",
    #     type=str,
    #     choices=TYPES,
    #     default=DEFAULT["tickers"][0]["type"],
    # )
    # parser.add_argument(
    #     "--volume",
    #     help="Plot the volume bar plot.",
    #     action="store_true",
    # )
    # parser.add_argument(
    #     "-f",
    #     "--flip",
    #     help="Flip the display.",
    #     action="store_true",
    # )
    # parser.add_argument(
    #     "--moving-average",
    #     help="Display a moving average.",
    #     type=int,
    #     dest="mav",
    # )
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


def load_config_values(args: Dict[str, Any]) -> Dict[str, Any]:
    """Update the args dictionary with values found in the config file."""
    # update the values if they are not None
    # allows for using other args to set values not set in the config file
    args.update({k: v for k, v in config.read(args["config"]).items() if v is not None})
    return args


def start_ticker_process(config_file: Path) -> multiprocessing.Process:
    """Create and start the ticker process.

    Args:
        args: dictionary containing the arguments.

    Returns:
        The ticker process.
    """
    tick_process = multiprocessing.Process(target=start_ticker, args=(config_file,))
    tick_process.start()
    return tick_process


def start_ticker(config_file: Path) -> None:
    """Start ticking.

    Args:
        args: dictionary containing the arguments.
    """
    logger.info("Starting ticker process")
    # Read config values
    args = config.read(config_file)

    display = Display(
        flip=args["flip"],
        model=args["epd_model"],
    )

    sequence = Sequence(
        [
            Ticker(api_key=args["api_key"], **ticker_kwargs)
            for ticker_kwargs in args["tickers"]
        ]
    )
    logger.debug(sequence)

    for (ticker, response) in sequence.start():
        try:
            if response["historical"] is None or response["historical"].empty:
                display.text(
                    f"No data for {ticker.symbol} in lookback range: {ticker.lookback}x{ticker.interval}",
                    show=True,
                    weight="bold",
                )
            else:
                logger.debug("API historical[0]: \n%s", response["historical"].iloc[0])
                logger.debug("API len(historical): %s", len(response["historical"]))
                logger.debug("API current_price: %s", response["current_price"])
                display.plot(
                    response["historical"],
                    response["current_price"],
                    top_string=f"{ticker.symbol}: $",
                    sub_string=f"{len(response['historical'])}x{ticker.interval}",
                    show=True,
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
    config_file = args.config

    if args.verbose > 0:
        set_verbosity(logger, args.verbose)

    # if the config file is not present, write the default values
    if not config_file.is_file():
        config.write_default(config_file)

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
