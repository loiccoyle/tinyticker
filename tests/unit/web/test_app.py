from pathlib import Path
from shutil import rmtree
from typing import Iterator

import pytest
from flask import Flask
from flask.testing import FlaskClient

from tinyticker.config import TinytickerConfig
from tinyticker.web.app import COMMANDS, create_app
from tinyticker.web.command import register

TT_CONFIG = TinytickerConfig()
TEST_DIR = Path("test_app")
LOG_FILE = TEST_DIR / "test_log.log"
CONFIG_FILE = TEST_DIR / "config.json"
TEST_COMMAND_RAN = False


@pytest.fixture()
def app() -> Iterator[Flask]:
    TEST_DIR = Path("test_app")
    if not TEST_DIR.is_dir():
        TEST_DIR.mkdir()
        LOG_FILE.touch()
    if not CONFIG_FILE.is_file():
        TT_CONFIG.to_file(CONFIG_FILE)

    app = create_app(CONFIG_FILE, log_dir=TEST_DIR)
    app.config.update(
        {
            "TESTING": True,
        }
    )
    yield app
    # cleanup
    rmtree(TEST_DIR)


@pytest.fixture()
def client(app: Flask) -> FlaskClient:
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


def test_index(client: FlaskClient):
    resp = client.get("/")
    assert resp.status_code == 200
    for ticker in TT_CONFIG.tickers:
        assert ticker.symbol in resp.data.decode("utf8")


def test_config(client: FlaskClient):
    params = {
        "symbol": ["AAPL", "GOOG"],
        "symbol_type": ["stock", "stock"],
        "plot_type": ["candle", "line"],
        "interval": ["1d", "1h"],
        "lookback": [30, 24],
        "wait_time": [10, 20],
        "mav": [3, ""],
        "volume": [1, ""],
        "avg_buy_price": ["", 100],
        "flip": True,
        "epd_model": "EPD_V3",
        "api_key": "SOMEKEY",
    }
    resp = client.get(
        "/config",
        query_string=params,
    )
    assert resp.status_code == 302
    assert resp.headers.get("location") == "/"
    new_config = TinytickerConfig.from_file(CONFIG_FILE)
    for key, value in params.items():
        if isinstance(value, list):
            assert [getattr(ticker, key) for ticker in new_config.tickers] == [
                v if v else None for v in value
            ]
        else:
            assert getattr(new_config, key) == value


def test_command(client: FlaskClient):
    old_commands = COMMANDS.copy()
    COMMANDS.clear()

    @register
    def test_cmd():
        global TEST_COMMAND_RAN
        TEST_COMMAND_RAN = True

    resp = client.get("/command", query_string={"command": "test cmd"})
    COMMANDS.update(old_commands)
    del COMMANDS["test cmd"]
    assert resp.status_code == 302
    assert resp.headers.get("location") == "/"
    assert TEST_COMMAND_RAN


def test_logs(client: FlaskClient):
    resp = client.get("logfiles")
    assert resp.status_code == 200
    assert LOG_FILE.name in resp.data.decode("utf8")
