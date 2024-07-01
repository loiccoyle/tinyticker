import pytest

from tinyticker.config import TickerConfig
from tinyticker.tickers.crypto import TickerCrypto

from ..utils import API_KEY
from .utils import assert_same_tick, assert_tick_expected, assert_tick_timing


@pytest.fixture
def config():
    return TickerConfig(
        symbol="BTC",
        symbol_type="crypto",
        interval="1h",
        lookback=24,
        wait_time=5,
    )


@pytest.fixture
def ticker(config):
    if API_KEY is None:
        raise ValueError("CRYPTOCOMPARE_API_KEY not set")
    return TickerCrypto(API_KEY, config)


def test_ticker_response(ticker, historical):
    assert_tick_expected(
        ticker,
        historical,
    )


def test_ticker_timing(ticker):
    assert_tick_timing(ticker)


def test_same_tick(ticker):
    assert_same_tick(ticker)


@pytest.mark.skipif(
    API_KEY is None,
    reason="No API key",
)
def test_empty():
    config = TickerConfig(
        symbol="INVALID",
        symbol_type="crypto",
        interval="1h",
        lookback=1,
    )
    if API_KEY is None:
        raise ValueError("CRYPTOCOMPARE_API_KEY not set")
    ticker = TickerCrypto(API_KEY, config)
    with pytest.raises(ValueError):
        ticker.single_tick()
