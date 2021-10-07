import json
import logging
import sys
from pathlib import Path

from flask import Flask, abort, redirect, render_template, request, send_from_directory

from .. import config as config_file
from ..settings import CONFIG_FILE

TEMPLATE_PATH = str(Path(__file__).parent / "templates")
LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


def create_app():
    app = Flask(__name__, template_folder=TEMPLATE_PATH)

    @app.after_request
    def add_header(response):
        response.cache_control.max_age = 0
        return response

    @app.route("/")
    def index():
        config = config_file.read()
        return render_template("index.html", config_file=str(CONFIG_FILE), **config)

    @app.route("/config")
    def config():
        LOGGER.debug("/config url args: %s", request.args)
        config = {}
        for key, value in request.args.items():
            if key in ["lookback"] and value == "":
                value = None
            elif key == "flip":
                value = True
            config[key] = value
        if "flip" not in config:
            config["flip"] = False
        LOGGER.debug("config dict: %s", config)
        config_file.write(config)
        return redirect("/", code=302)

    @app.route("/command")
    def command():
        LOGGER.info("/command url args: %s", request.args)
        return redirect("/", code=302)

    @app.route("/img/favicon.ico")
    def favicon():
        LOGGER.info("Returning 404 for favicon request")
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


def main():
    LOGGER.info("Starting tinyticker-web")
    app = create_app()
    app.run(host="0.0.0.0", port=8000, debug=False, threaded=True)
    LOGGER.info("Stopping tinyticker-web")
