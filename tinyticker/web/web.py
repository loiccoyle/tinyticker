import argparse
import logging
import sys
from pathlib import Path
from typing import List

from flask import Flask, abort, redirect, render_template, request, send_from_directory

from .. import config as config_file
from ..settings import CONFIG_FILE
from . import logger
from .command import COMMANDS

TEMPLATE_PATH = str(Path(__file__).parent / "templates")


def create_app():
    app = Flask(__name__, template_folder=TEMPLATE_PATH)

    @app.after_request
    def add_header(response):
        response.cache_control.max_age = 0
        return response

    @app.route("/")
    def index():
        config = config_file.read()
        return render_template(
            "index.html",
            config_file=str(CONFIG_FILE),
            commands=COMMANDS.keys(),
            **config
        )

    @app.route("/config")
    def config():
        logger.debug("/config url args: %s", request.args)
        config = {}
        for key, value in request.args.items():
            if key in ["lookback"] and value == "":
                value = None
            elif key == "flip":
                value = True
            config[key] = value
        if "flip" not in config:
            config["flip"] = False
        logger.debug("config dict: %s", config)
        config_file.write(config)
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

    logger.info("Starting tinyticker-web")
    app = create_app()
    app.run(host="0.0.0.0", port=args.port, debug=False, threaded=True)
    logger.info("Stopping tinyticker-web")
