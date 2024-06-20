from pathlib import Path
from unittest import TestCase

import pandas as pd
import pytest

from tinyticker.config import TickerConfig
from tinyticker.tickers.stock import TickerStock

from .utils import assert_same_tick, assert_tick_expected, assert_tick_timing


class TestTickerStock(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data_dir = Path(__file__).parents[2] / "data"
        cls.historical_path = cls.data_dir / "stock_historical.pkl"
        cls.historical: pd.DataFrame = pd.read_pickle(cls.historical_path)
        cls.config = TickerConfig(
            symbol="SPY",
            symbol_type="stock",
            interval="1d",
            lookback=30,
            wait_time=5,
        )
        cls.ticker = TickerStock(cls.config)

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
        config = TickerConfig(
            symbol="INVALID",
            symbol_type="stock",
            interval="1h",
            lookback=1,
        )
        with pytest.raises(KeyError):
            ticker = TickerStock(config)
            ticker.single_tick()
