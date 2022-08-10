import argparse
import logging
import sys
from pathlib import Path
from typing import List

from .. import config as cfg
from ..display import Display
from ..settings import CONFIG_FILE, LOG_DIR, generate_qrcode, set_verbosity
from ..utils import RawTextArgumentDefaultsHelpFormatter
from ..waveshare_lib.models import MODELS
from .app import create_app
from .app import logger as logger_app

logger = logging.getLogger(__name__)


def parse_args(args: List[str]) -> argparse.Namespace:
    """Parse the command line arguments.

    Args:
        args: The command line argument.

    Returns:
        The parsed arguments.
    """
    parser = argparse.ArgumentParser(
        prog="tinyticker-web",
        description="tinyticker web interface.",
        formatter_class=RawTextArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-p",
        "--port",
        default=7104,
        type=int,
        help="Port number.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Verbosity.",
        action="count",
        default=0,
    )
    parser.add_argument(
        "-c",
        "--config",
        help="Config file.",
        type=Path,
        default=CONFIG_FILE,
    )
    parser.add_argument(
        "-q",
        "--show-qrcode",
        help="Display a qrcode containing the URL of the dashboard and exit.",
        action="store_true",
    )
    parser.add_argument(
        "--log-dir",
        help="Directory containing tinyticker's log files.",
        type=Path,
        default=LOG_DIR,
    )
    return parser.parse_args(args)


def main():
    args = parse_args(sys.argv[1:])
    if args.verbose > 0:
        set_verbosity(logger, args.verbose)
        set_verbosity(logger_app, args.verbose)

    logger.debug("Args: %s", args)

    if not args.log_dir.is_dir():
        args.log_dir.mkdir(parents=True)

    if args.show_qrcode:
        logger.info("Generating qrcode.")
        config = {**cfg.DEFAULT, **cfg.read(args.config)}
        epd_model = MODELS[config["epd_model"]]
        qrcode = generate_qrcode(
            epd_model.width,
            epd_model.height,
            args.port,
        )
        display = Display(
            model=config["epd_model"],
            flip=config["flip"],
        )
        logger.info("Displaying qrcode.")
        display.show_image(qrcode)
        del display
        sys.exit()

    logger.info("Starting tinyticker-web")
    app = create_app(config_file=args.config, log_dir=args.log_dir)
    app.run(host="0.0.0.0", port=args.port, debug=False, threaded=True)
    logger.info("Stopping tinyticker-web")


if __name__ == "__main__":
    main()
