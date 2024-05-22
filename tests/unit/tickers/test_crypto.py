import os
from pathlib import Path
from unittest import TestCase

import pandas as pd
import pytest

from tinyticker.config import TickerConfig
from tinyticker.tickers.crypto import TickerCrypto

from .utils import assert_same_tick, assert_tick_expected, assert_tick_timing

API_KEY = os.environ.get("CRYPTOCOMPARE_API_KEY", None)


class TestTickerCrypto(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if API_KEY is None:
            raise ValueError("CRYPTOCOMPARE_API_KEY not set")
        cls.data_dir = Path(__file__).parents[2] / "data"
        cls.historical_path = cls.data_dir / "crypto_historical.pkl"
        cls.historical: pd.DataFrame = pd.read_pickle(cls.historical_path)
        cls.config = TickerConfig(
            symbol="BTC",
            symbol_type="crypto",
            interval="1h",
            lookback=24,
            wait_time=5,
        )
        cls.ticker = TickerCrypto(API_KEY, cls.config)

    def test_ticker_response(self):
        assert_tick_expected(
            self.ticker,
            self.historical,
        )

    def test_ticker_timing(self):
        assert_tick_timing(self.ticker)

    def test_same_tick(self):
        assert_same_tick(self.ticker)

    def test_empty(self):
        if API_KEY is None:
            raise ValueError("CRYPTOCOMPARE_API_KEY not set")
        config = TickerConfig(
            symbol="INVALID",
            symbol_type="crypto",
            interval="1h",
            lookback=1,
        )
        ticker = TickerCrypto(API_KEY, config)
        with pytest.raises(ValueError):
            ticker.single_tick()
