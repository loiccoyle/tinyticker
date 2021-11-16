import argparse
import sys
from pathlib import Path
from socket import timeout
from typing import List
from urllib.error import HTTPError, URLError

from flask import Flask, abort, redirect, render_template, request, send_from_directory

from .. import __version__
from .. import config as cfg
from ..display import Display
from ..settings import CONFIG_FILE, generate_qrcode, set_verbosity
from ..ticker import INTERVAL_LOOKBACKS, INTERVAL_TIMEDELTAS, SYMBOL_TYPES
from ..utils import RawTextArgumentDefaultsHelpFormatter, check_for_update
from ..waveshare_lib.models import MODELS
from . import logger
from .command import COMMANDS, restart

TEMPLATE_PATH = str(Path(__file__).parent / "templates")

INTERVAL_WAIT_TIMES = {k: v.value * 1e-9 for k, v in INTERVAL_TIMEDELTAS.items()}  # type: ignore


def create_app(config_file: Path = CONFIG_FILE) -> Flask:
    """Create the flask app.

    Args:
        config_file: config file to read from and write to.

    Returns:
        The flask application.
    """
    app = Flask(__name__, template_folder=TEMPLATE_PATH)

    @app.after_request
    def add_header(response):
        response.cache_control.max_age = 0
        return response

    @app.route("/")
    def index():
        config = {**cfg.DEFAULT, **cfg.read(config_file)}
        commands = sorted(COMMANDS.keys())
        # remove the update command as we treat it separately
        commands.remove("update")
        # TODO: performing this query on the server will reduce responsiveness
        try:
            update_available = check_for_update(timeout=1)
            logger.info("Update available: %s", update_available)
        except (HTTPError, URLError, timeout):
            update_available = False
            logger.warning("Update check failed", exc_info=True)
        return render_template(
            "index.html",
            cfg=config_file,
            commands=commands,
            type_options=cfg.TYPES,
            symbol_type_options=SYMBOL_TYPES,
            interval_lookbacks=INTERVAL_LOOKBACKS,
            interval_wait_times=INTERVAL_WAIT_TIMES,
            interval_options=INTERVAL_LOOKBACKS.keys(),
            epd_model_options=MODELS.values(),
            update_available=update_available,
            version=__version__,
            **config,
        )

    @app.route("/config")
    def config():
        logger.debug("/config url args: %s", request.args)
        config = {}
        for key, value in request.args.items():
            if key in ["api_key"] and value == "":
                value = None
            elif key in ["lookback", "wait_time", "mav"]:
                if value == "":
                    value = None
                else:
                    value = int(value)
            elif key == "flip":
                value = True
            config[key] = value
        if "flip" not in config:
            config["flip"] = False
        logger.debug("config dict: %s", config)
        cfg.write(config, config_file)
        # restart
        restart()
        return redirect("/", code=302)

    @app.route("/command")
    def command():
        logger.debug("/command url args: %s", request.args)
        command = request.args.get("command")
        if command:
            # call the registered command function
            COMMANDS.get(command, lambda: None)()

        return redirect("/", code=302)

    @app.route("/img/favicon.ico")
    def favicon():
        logger.info("Returning 404 for favicon request")
        abort(404)

    @app.route("/img/<path:path>")
    def send_image(path):
        return send_from_directory(TEMPLATE_PATH + "/images", path)

    @app.route("/js/<path:path>")
    def send_js(path):
        return send_from_directory(TEMPLATE_PATH + "/js", path)

    @app.route("/css/<path:path>")
    def send_css(path):
        return send_from_directory(TEMPLATE_PATH + "/css", path)

    @app.errorhandler(500)
    def internal_error(error):
        sys.exit(1)

    return app


def parse_args(args: List[str]) -> argparse.Namespace:
    """Parse the command line arguments.

    Args:
        args: The command line argument.

    Returns:
        The parsed arguments.
    """
    parser = argparse.ArgumentParser(
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
    return parser.parse_args(args)


def main():
    args = parse_args(sys.argv[1:])
    if args.verbose > 0:
        set_verbosity(logger, args.verbose)

    logger.debug("Args: %s", args)

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
    app = create_app(args.config)
    app.run(host="0.0.0.0", port=args.port, debug=False, threaded=True)
    logger.info("Stopping tinyticker-web")
