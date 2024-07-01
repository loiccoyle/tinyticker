from pathlib import Path
from unittest import TestCase

import pandas as pd
import pytest

from tinyticker.config import TickerConfig
from tinyticker.tickers.stock import TickerStock

from .utils import assert_same_tick, assert_tick_expected, assert_tick_timing


@pytest.fixture
def config():
    return TickerConfig(
        symbol="SPY",
        symbol_type="stock",
        interval="1d",
        lookback=30,
        wait_time=5,
    )


@pytest.fixture
def ticker(config):
    return TickerStock(config)


def test_ticker_response(ticker, historical):
    assert_tick_expected(
        ticker,
        historical,
    )


def test_ticker_timing(ticker):
    assert_tick_timing(ticker)


def test_same_tick(ticker):
    assert_same_tick(ticker)


def test_empty():
    config = TickerConfig(
        symbol="INVALID",
        symbol_type="stock",
        interval="1h",
        lookback=1,
    )
    ticker = TickerStock(config)
    with pytest.raises(ValueError):
        ticker.single_tick()
