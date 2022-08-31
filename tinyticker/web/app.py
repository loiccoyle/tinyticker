import logging
import socket
import subprocess
import sys
from pathlib import Path
from socket import timeout
from typing import Optional
from urllib.error import HTTPError, URLError

from flask import Flask, abort, redirect, render_template, request, send_from_directory

from .. import __version__
from .. import config as cfg
from ..settings import CONFIG_FILE, LOG_DIR
from ..ticker import INTERVAL_LOOKBACKS, INTERVAL_TIMEDELTAS, SYMBOL_TYPES
from ..utils import check_for_update
from ..waveshare_lib.models import MODELS
from .command import COMMANDS, reboot, refresh

logger = logging.getLogger(__name__)

TEMPLATE_PATH = str(Path(__file__).parent / "templates")

INTERVAL_WAIT_TIMES = {k: v.value * 1e-9 for k, v in INTERVAL_TIMEDELTAS.items()}


def no_empty_str(data: str) -> Optional[str]:
    if data == "":
        return None
    return data


def no_empty_int(data: str) -> Optional[int]:
    if data == "":
        return None
    return int(data)


def str_to_bool(data: str) -> Optional[bool]:
    if data == "1":
        return True
    elif data == "0":
        return False
    return None


def create_app(config_file: Path = CONFIG_FILE, log_dir: Path = LOG_DIR) -> Flask:
    """Create the flask app.

    Args:
        config_file: config file to read from and write to.

    Returns:
        The flask application.
    """
    app = Flask(__name__, template_folder=TEMPLATE_PATH)
    commands = sorted(COMMANDS.keys())
    # remove the update command as we treat it separately
    commands.remove("update")
    log_files = sorted([path.name for path in log_dir.glob("*.log")])
    hostname = socket.gethostname()

    @app.after_request
    def add_header(response):
        response.cache_control.max_age = 0
        return response

    @app.route("/")
    def index():
        config = {**cfg.DEFAULT, **cfg.read(config_file)}
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
            hostname=hostname,
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

    @app.route("/logfiles")
    def logs():
        return render_template("logfiles.html", log_files=log_files)

    @app.route("/config")
    def config():
        logger.debug("/config url args: %s", request.args)
        config = {}
        config["api_key"] = request.args.get("api_key", type=no_empty_str)
        config["flip"] = request.args.get("flip", default=False, type=bool)
        config["epd_model"] = request.args.get("epd_model")
        # ticker_args = cfg.DEFAULT["tickers"].keys()
        tickers = {}
        tickers["symbol"] = request.args.getlist("symbol")
        tickers["symbol_type"] = request.args.getlist("symbol_type")
        tickers["type"] = request.args.getlist("type")
        tickers["interval"] = request.args.getlist("interval")
        tickers["lookback"] = request.args.getlist("lookback", type=no_empty_int)
        tickers["wait_time"] = request.args.getlist("wait_time", type=no_empty_int)
        tickers["mav"] = request.args.getlist("mav", type=no_empty_int)
        tickers["volume"] = request.args.getlist("volume", type=str_to_bool)

        # invert the ticker dict of list to list of dict
        config["tickers"] = [dict(zip(tickers, t)) for t in zip(*tickers.values())]
        logger.debug(config)
        cfg.write(config, config_file)
        refresh()
        return redirect("/", code=302)

    @app.route("/command")
    def command():
        logger.debug("/command url args: %s", request.args)
        command = request.args.get("command")
        if command:
            # call the registered command function
            COMMANDS.get(command, lambda: None)()
        return redirect("/", code=302)

    @app.route("/set_hostname")
    def set_hostname():
        logger.debug("/host_rename url args: %s", request.args)
        hostname = request.args.get("hostname")
        if hostname:
            subprocess.Popen(
                f"sudo echo {hostname} | sudo tee /etc/hostname", shell=True
            )
            subprocess.Popen(
                f"sudo echo 127.0.0.1\t{hostname} | sudo tee /etc/hosts",
                shell=True,
            )
            if Path("/etc/comitup.conf").exists():
                subprocess.Popen(
                    f"sudo sed -i 's/^ap_name:.*/ap_name: {hostname}/' /etc/comitup.conf",
                    shell=True,
                )
            reboot()
        return redirect("/", code=302)

    # @app.route("/img/favicon.ico")
    # def favicon():
    #     logger.info("Returning 404 for favicon request")
    #     abort(404)

    @app.route("/get-log/<log_file_name>")
    def send_log(log_file_name):
        if log_file_name not in log_files:
            abort(404)
        try:
            logger.info("Loading log file %s", log_dir / log_file_name)
            return send_from_directory(log_dir, log_file_name)
        except FileNotFoundError:
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
