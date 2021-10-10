import argparse
import logging
import sys
from pathlib import Path
from typing import List

from flask import Flask, abort, redirect, render_template, request, send_from_directory

from .. import config as config_file
from ..settings import CONFIG_FILE, set_verbosity
from ..ticker import INTERVAL_LOOKBACKS, INTERVAL_TIMEDELTAS, SYMBOL_TYPES
from . import logger
from .command import COMMANDS

TEMPLATE_PATH = str(Path(__file__).parent / "templates")

INTERVAL_WAIT_TIMES = {k: v.value * 1e-9 for k, v in INTERVAL_TIMEDELTAS.items()}  # type: ignore


def create_app():
    app = Flask(__name__, template_folder=TEMPLATE_PATH)

    @app.after_request
    def add_header(response):
        response.cache_control.max_age = 0
        return response

    @app.route("/")
    def index():
        config = {**config_file.DEFAULT, **config_file.read()}
        return render_template(
            "index.html",
            config_file=str(CONFIG_FILE),
            commands=COMMANDS.keys(),
            type_options=config_file.TYPES,
            symbol_type_options=SYMBOL_TYPES,
            interval_lookbacks=INTERVAL_LOOKBACKS,
            interval_wait_times=INTERVAL_WAIT_TIMES,
            interval_options=INTERVAL_LOOKBACKS.keys(),
            **config,
        )

    @app.route("/config")
    def config():
        logger.debug("/config url args: %s", request.args)
        config = {}
        for key, value in request.args.items():
            if key in ["api_key"] and value == "":
                value = None
            elif key in ["lookback", "wait_time"]:
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
        config_file.write(config)
        # restart
        COMMANDS["restart"]()
        return redirect("/", code=302)

    @app.route("/command")
    def command():
        logger.debug("/command url args: %s", request.args)
        command = request.args.get("command")
        if command:
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
    parser = argparse.ArgumentParser(description="tinyticker web interface.")
    parser.add_argument("-p", "--port", default=8000, type=int, help="Port number.")
    parser.add_argument("-v", "--verbose", help="Verbosity.", action="count", default=0)
    return parser.parse_args(args)


def main():
    args = parse_args(sys.argv[1:])
    # refactor this with the other verbosity control
    if args.verbose > 0:
        set_verbosity(logger, args.verbose)

    logger.debug("Args: %s", args)

    logger.info("Starting tinyticker-web")
    app = create_app()
    app.run(host="0.0.0.0", port=args.port, debug=False, threaded=True)
    logger.info("Stopping tinyticker-web")
