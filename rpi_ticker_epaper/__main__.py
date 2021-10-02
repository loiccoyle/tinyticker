import argparse
import logging
import sys
from typing import List

from . import logger
from .display import Display
from .settings import I2C_ADDRESS
from .ticker import Ticker


class RawTextArgumentDefaultsHelpFormatter(
    argparse.RawTextHelpFormatter, argparse.ArgumentDefaultsHelpFormatter
):
    pass


def parse_args(args: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="""Raspberry Pi crypto ticker using an LCD display.

Note:
    Make sure i2c is enabled on your RPi.
    To avoid permissions errors add the user to the i2c group.
    Find your i2c address using i2cdetect -y 0 or i2cdetect -y 1.
""",
        formatter_class=RawTextArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-c", "--coin", help="Crypto coins.", type=str, nargs=2, default=["BTC", "ETH"]
    )
    parser.add_argument(
        "-C", "--currency", help="Display currency.", type=str, default="USD"
    )
    parser.add_argument(
        "-w", "--wait-time", help="Wait time, in seconds.", type=int, default=120
    )
    parser.add_argument(
        "-f",
        "--string-format",
        help="Python format string.",
        type=str,
        default="{delta}{coin}:{currency} {price}",
    )
    parser.add_argument(
        "-i",
        "--i2c-address",
        help="I2C address of the backpack.",
        type=int,
        default=I2C_ADDRESS,
    )
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

    display = Display(args.i2c_address, string_format=args.string_format)
    ticker = Ticker(args.api_key, args.wait_time)

    for response in ticker.tick(args.coin, args.currency):
        if response is None:
            display.lcd.set("API Error     :(", 1)
            display.lcd.set("Check internet.", 2)
        else:
            logger.debug("API response: %s", response)
            display.show(response)
