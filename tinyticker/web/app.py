import logging
import socket
import subprocess
import sys
import threading
from pathlib import Path
from typing import Optional

from flask import Flask, abort, redirect, render_template, request, send_from_directory

from .. import __version__
from ..config import PLOT_TYPES, SequenceConfig, TickerConfig, TinytickerConfig
from ..paths import CONFIG_FILE, LOG_DIR
from ..ticker import INTERVAL_LOOKBACKS, INTERVAL_TIMEDELTAS, SYMBOL_TYPES
from ..waveshare_lib.models import MODELS
from .command import COMMANDS, reboot

LOGGER = logging.getLogger(__name__)
TEMPLATE_PATH = str(Path(__file__).parent / "templates")
INTERVAL_WAIT_TIMES = {k: v.value * 1e-9 for k, v in INTERVAL_TIMEDELTAS.items()}


def no_empty_str(data: str) -> Optional[str]:
    if data == "":
        return None
    return data


def no_empty_float(data: str) -> Optional[float]:
    if data == "":
        return None
    return float(data)


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
        log_dir: directory containing the log files.

    Returns:
        The flask application.
    """
    app = Flask(__name__, template_folder=TEMPLATE_PATH)
    # don't keep update as we handle is differently
    commands = {cmd.name: cmd.desc for cmd in COMMANDS.values() if cmd.name != "update"}
    log_files = sorted([path.name for path in log_dir.glob("*.log")])
    hostname = socket.gethostname()

    @app.after_request
    def add_header(response):
        response.cache_control.max_age = 0
        return response

    @app.route("/")
    def index():
        tt_config = TinytickerConfig.from_file(config_file)
        return render_template(
            "index.html",
            hostname=hostname,
            commands=commands,
            plot_type_options=PLOT_TYPES,
            symbol_type_options=SYMBOL_TYPES,
            interval_lookbacks=INTERVAL_LOOKBACKS,
            interval_wait_times=INTERVAL_WAIT_TIMES,
            interval_options=INTERVAL_LOOKBACKS.keys(),
            epd_model_options=MODELS.values(),
            version=__version__,
            **tt_config.to_dict(),
        )

    @app.route("/logfiles")
    def logs():
        return render_template("logfiles.html", log_files=log_files)

    @app.route("/config")
    def config():
        # TODO: post the config via a json post instead of parsing it here
        # Something like:
        # https://stackoverflow.com/questions/22195065/how-to-send-a-json-object-using-html-form-data
        LOGGER.debug("/config url args: %s", request.args)
        tickers = {}
        tickers["symbol"] = request.args.getlist("symbol")
        tickers["symbol_type"] = request.args.getlist("symbol_type")
        tickers["plot_type"] = request.args.getlist("plot_type")
        tickers["interval"] = request.args.getlist("interval")
        tickers["lookback"] = request.args.getlist("lookback", type=no_empty_int)
        tickers["wait_time"] = request.args.getlist("wait_time", type=no_empty_int)
        tickers["mav"] = request.args.getlist("mav", type=no_empty_int)
        tickers["volume"] = request.args.getlist("volume", type=str_to_bool)
        tickers["avg_buy_price"] = request.args.getlist(
            "avg_buy_price", type=no_empty_float
        )

        sequence = SequenceConfig(
            skip_outdated=request.args.get("skip_outdated", False, type=bool),
            # NOTE: currently not toggleable from the web app
            skip_empty=request.args.get("skip_empty", True, type=bool),
        )

        # invert the ticker dict of list to list of dict and create ticker list
        tickers = [
            TickerConfig(**dict(zip(tickers, t))) for t in zip(*tickers.values())
        ]
        tt_config = TinytickerConfig(
            api_key=request.args.get("api_key", type=no_empty_str),
            flip=request.args.get("flip", default=False, type=bool),
            epd_model=request.args.get("epd_model", "EPD_v3"),
            tickers=tickers,
            sequence=sequence,
        )
        LOGGER.debug(tt_config)
        # writing the config to file, the main ticker process is monitoring this file
        # and will refresh the ticker process
        tt_config.to_file(config_file)
        return redirect("/", code=302)

    @app.route("/command")
    def command():
        LOGGER.debug("/command url args: %s", request.args)
        command = request.args.get("command")
        if command:
            # call the registered command function in a separate thread
            cmd = COMMANDS.get(command, None)
            if cmd is not None:
                threading.Thread(target=cmd.func).start()
        return redirect("/", code=302)

    @app.route("/set_hostname")
    def set_hostname():
        LOGGER.debug("/host_rename url args: %s", request.args)
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

    @app.route("/get-log/<log_file_name>")
    def send_log(log_file_name):
        if log_file_name not in log_files:
            abort(404)
        try:
            LOGGER.info("Loading log file %s", log_dir / log_file_name)
            return send_from_directory(log_dir, log_file_name, mimetype="text/plain")
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
    def internal_error(_):
        sys.exit(1)

    return app
