import argparse
import atexit
import os
import signal
import subprocess
import sys
from pathlib import Path
from typing import List

from . import __version__, config, logger
from .config import DEFAULT, TYPES
from .display import Display
from .settings import CONFIG_FILE, PID_FILE, set_verbosity, start_on_boot
from .ticker import INTERVAL_LOOKBACKS, SYMBOL_TYPES, Ticker
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
        "--epd-model",
        help="ePaper display model.",
        type=str,
        default="EPD_v2",
        choices=MODELS.keys(),
    )
    parser.add_argument(
        "--symbol-type",
        help="The type of the symbol.",
        type=str,
        default="stock",
        choices=SYMBOL_TYPES,
    )
    parser.add_argument(
        "-a",
        "--api-key",
        help="CryptoCompare API key, https://min-api.cryptocompare.com/pricing.",
        type=str,
        default=DEFAULT["api_key"],
    )
    parser.add_argument(
        "-s",
        "--symbol",
        help="Asset symbol.",
        type=str,
        default=DEFAULT["symbol"],
    )
    parser.add_argument(
        "-i",
        "--interval",
        help="Interval.",
        type=str,
        default=DEFAULT["interval"],
        choices=INTERVAL_LOOKBACKS.keys(),
    )
    parser.add_argument(
        "-l",
        "--lookback",
        help="Look back amount.",
        type=int,
        default=DEFAULT["lookback"],
    )
    parser.add_argument(
        "-w",
        "--wait-time",
        help="Wait time in seconds.",
        type=int,
        default=DEFAULT["wait_time"],
    )
    parser.add_argument(
        "-t",
        "--type",
        help="Plot style, see mplfinance.",
        type=str,
        default=DEFAULT["type"],
        choices=TYPES,
    )
    parser.add_argument(
        "-f",
        "--flip",
        help="Flip the display.",
        action="store_true",
    )
    parser.add_argument(
        "--moving-average",
        help="Display a moving average.",
        type=int,
        dest="mav",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Verbosity.",
        action="count",
        default=0,
    )
    parser.add_argument(
        "--config",
        help=f"Take values from config file.",
        nargs="?",
        type=Path,
        const=CONFIG_FILE,
        default=None,
    )
    parser.add_argument(
        "--start-on-boot",
        help="Create and enable the systemd service files, then exits. Will require sudo.",
        action="store_true",
    )
    parser.add_argument(
        "--version",
        help="Show the version and exit.",
        action="version",
        version="%(prog)s {version}".format(version=__version__),
    )
    return parser.parse_args(args)


def main():
    args = parse_args(sys.argv[1:])
    args = vars(args)

    if args["verbose"] > 0:
        set_verbosity(logger, args["verbose"])

    if args["config"]:
        # if the config file is not present, write the default values
        if not args["config"].is_file():
            config.write_default(args["config"])
        # update the values if they are not None
        # allows for using other args to set values not set in the config file
        args.update(
            {k: v for k, v in config.read(args["config"]).items() if v is not None}
        )

    if args["start_on_boot"]:
        logger.info("Creating and enabling systemd unit files.")

        if os.geteuid() == 0:
            start_on_boot()
        else:
            logger.info("No sudo access, trying with sudo.")
            subprocess.check_call(["sudo", sys.executable] + sys.argv)
        sys.exit()

    pid = os.getpid()
    logger.info("PID: %s", pid)
    if not PID_FILE.parent.is_dir():
        PID_FILE.parent.mkdir(parents=True, exist_ok=True)
    PID_FILE.write_text(str(pid))

    logger.debug("Args: %s", args)

    display = Display(
        flip=args["flip"],
        model=args["epd_model"],
    )
    ticker = Ticker(
        symbol_type=args["symbol_type"],
        api_key=args["api_key"],
        symbol=args["symbol"],
        interval=args["interval"],
        lookback=args["lookback"],
        wait_time=args["wait_time"],
    )

    #  setup signal handlers
    def cleanup(display: Display):
        logger.info("Exiting.")
        if PID_FILE.is_file():
            PID_FILE.unlink()
        del display

    atexit.register(cleanup, display)

    def restart(*_) -> None:
        logger.info("Restarting.")
        os.execv(sys.argv[0], sys.argv)

    signal.signal(signal.SIGUSR1, restart)

    for response in ticker.tick():
        try:
            if response["historical"] is None or response["historical"].empty:
                error_str = f"No data in lookback range: {ticker.lookback}x{args['interval']} :("
                logger.debug(error_str)
                display.text(
                    error_str,
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
                    top_string=f"{args['symbol']}: $",
                    sub_string=f"{len(response['historical'])}x{args['interval']}",
                    type=args["type"],
                    mav=args["mav"],
                    show=True,
                )
        except Exception as exc:
            logger.error(exc, stack_info=True)
            display.text("Wooops something broke :(", show=True, weight="bold")


if __name__ == "__main__":
    main()
