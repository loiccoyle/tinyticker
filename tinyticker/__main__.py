import argparse
import logging
import sys
import os
from typing import List

from . import logger
from .display import Display
from .ticker import Ticker
from .settings import PID_FILE


class RawTextArgumentDefaultsHelpFormatter(
    argparse.RawTextHelpFormatter, argparse.ArgumentDefaultsHelpFormatter
):
    pass


def parse_args(args: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="""Raspberry Pi crypto ticker using an LCD display.

Note:
    Make sure SPI is enabled on your RPi.
""",
        formatter_class=RawTextArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("-c", "--coin", help="Crypto coin.", type=str, default="BTC")
    parser.add_argument(
        "-C", "--currency", help="Display currency.", type=str, default="USD"
    )
    parser.add_argument(
        "-i",
        "--interval",
        help="Interval.",
        type=str,
        default="hour",
        choices=["day", "hour", "minute"],
    )
    parser.add_argument(
        "-l", "--look-back", help="Look back amount.", type=int, default=None
    )
    parser.add_argument(
        "-w", "--wait-time", help="Wait time in seconds.", type=int, default=None
    )
    parser.add_argument("-f", "--flip", help="Flip the display.", action="store_true")

    parser.add_argument("-v", "--verbose", help="Verbosity.", action="count", default=0)
    parser.add_argument(
        "api_key",
        help="CryptoCompare API key, https://min-api.cryptocompare.com/pricing.",
        type=str,
    )
    return parser.parse_args(args)


def main():
    args = parse_args(sys.argv[1:])
    if args.verbose > 0:
        verbose_map = {1: logging.INFO, 2: logging.DEBUG}
        level = verbose_map[args.verbose]
        # from https://docs.python.org/3/howto/logging.html#configuring-logging
        logger.setLevel(level)
        # create console handler and set level to debug
        handler = logging.StreamHandler()
        handler.setLevel(level)
        # create formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        # add formatter to handler
        handler.setFormatter(formatter)
        # add ch to logger
        logger.addHandler(handler)

    logger.debug("Args: %s", args)

    display = Display(
        args.coin,
        args.currency,
        flip=args.flip,
    )
    ticker = Ticker(
        args.api_key,
        coin=args.coin,
        currency=args.currency,
        interval=args.interval,
        look_back=args.look_back,
        wait_time=args.wait_time,
    )

    with open(PID_FILE, "+a") as pid_file:
        pid = os.getpid()
        logger.info("PID: %s", pid)
        pid_file.write(str(pid))

    try:
        for historical, current in ticker.tick():
            logger.debug("API response[0]: %s", historical[0])
            logger.debug("API len(response): %s", len(historical))
            display.plot(
                historical,
                current,
                sub_string=f"{ticker.look_back} {args.interval}s",
                show=True,
            )
    except Exception as e:
        logger.error(e, stack_info=True)
        display.text(str(e), show=True)
    finally:
        logger.info("Exiting")
        del display
        PID_FILE.unlink()