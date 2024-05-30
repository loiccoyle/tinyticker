from pathlib import Path
from shutil import rmtree
from typing import Iterator

import pytest
from flask import Flask
from flask.testing import FlaskClient

from tinyticker.config import (
    TinytickerConfig,
    TickerConfig,
    LayoutConfig,
    SequenceConfig,
)
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
    expected_config = TinytickerConfig(
        tickers=[
            TickerConfig(
                symbol="AAPL",
                symbol_type="stock",
                plot_type="candle",
                interval="1d",
                lookback=30,
                wait_time=10,
                mav=3,
                volume=True,
                avg_buy_price=None,
                prepost=True,
                layout=LayoutConfig(name="default", y_axis=True, x_gaps=False),
            ),
            TickerConfig(
                symbol="GOOG",
                symbol_type="stock",
                plot_type="line",
                interval="1h",
                lookback=24,
                wait_time=20,
                mav=None,
                volume=False,
                avg_buy_price=100.0,
                prepost=False,
                layout=LayoutConfig(name="big_price", y_axis=False, x_gaps=True),
            ),
        ],
        flip=True,
        epd_model="EPD_V3",
        api_key="SOMEKEY",
        sequence=SequenceConfig(
            skip_outdated=False,
            skip_empty=True,
        ),
    )
    resp = client.post(
        "/config",
        headers={"Content-Type": "application/json"},
        data=expected_config.to_json(),
    )
    assert resp.status_code == 302
    assert resp.headers.get("location") == "/"
    new_config = TinytickerConfig.from_file(CONFIG_FILE)
    assert new_config == expected_config


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
