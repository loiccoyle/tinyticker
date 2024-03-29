import os
import time
from datetime import timezone
from pathlib import Path
from typing import Optional
from unittest import TestCase

import numpy as np
import pandas as pd
import pytest
import pytz

from tinyticker import utils
from tinyticker import config, ticker

# monkey patch the now function to be time indenpendent
utils.__dict__["now"] = lambda: pd.Timestamp(
    2021, 7, 22, 18, 00, 00, tzinfo=timezone.utc
)

API_KEY = os.environ.get("CRYPTOCOMPARE_API_KEY", None)


def same(df1: pd.DataFrame, df2: pd.DataFrame) -> bool:
    return np.allclose(df1.to_numpy(), df2.to_numpy())


class TestTicker(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data_dir = Path(__file__).parents[1] / "data"
        cls.stock_historical_path = cls.data_dir / "stock_historical.pkl"
        cls.crypto_historical_path = cls.data_dir / "crypto_historical.pkl"
        cls.stock_historical: pd.DataFrame = pd.read_pickle(cls.stock_historical_path)
        cls.crypto_historical: pd.DataFrame = pd.read_pickle(cls.crypto_historical_path)
        cls.stock_ticker = ticker.Ticker(
            symbol="SPY",
            symbol_type="stock",
            api_key=None,
            interval="1d",
            lookback=30,
            wait_time=None,
        )
        cls.crypto_ticker = ticker.Ticker(
            symbol_type="crypto",
            symbol="BTC",
            api_key=API_KEY,
            interval="1h",
            lookback=24,
            wait_time=None,
        )

    def test_stock_ticker_response(self):
        self._test_ticker_response(
            self.stock_ticker,
            self.stock_historical,
        )

    def test_crypto_ticker_response(self):
        self._test_ticker_response(
            self.crypto_ticker,
            self.crypto_historical,
        )

    def _test_ticker_response(
        self,
        ticker: ticker.Ticker,
        expected: pd.DataFrame,
        overwrite_path: Optional[Path] = None,
    ):
        resp = ticker.single_tick()
        # used to update the expected data files
        if overwrite_path is not None:
            resp.historical.to_pickle(overwrite_path)
        assert isinstance(resp.historical, pd.DataFrame)
        assert resp.current_price is not None
        assert {"Open", "Close", "High", "Low", "Volume"}.issubset(
            set(resp.historical.columns)
        )
        assert resp.historical.index.inferred_type == "datetime64"
        assert len(resp.historical) == ticker.lookback
        assert ticker.wait_time == pd.to_timedelta(ticker.interval).total_seconds()
        assert resp.historical.index.tzinfo == pytz.UTC  # type: ignore
        assert (resp.historical.index == expected.index).all()
        assert (resp.historical.columns == expected.columns).all()
        # assert same(resp.historical, expected)

    def test_crypto_ticker_tick(self):
        self._test_ticker_tick(self.crypto_ticker)

    def test_stock_ticker_tick(self):
        self._test_ticker_tick(self.stock_ticker)

    def _test_ticker_tick(self, ticker: ticker.Ticker):
        # these two should return the same data because we monkey patched
        resp = ticker.single_tick()
        gen = ticker.tick()
        tick = next(gen)
        # assert resp.current_price == tick.current_price
        assert (resp.historical.index == tick.historical.index).all()
        assert same(resp.historical, tick.historical)

    def test_stock_ticker_timing(self):
        self._test_ticker_timing(self.stock_ticker)

    def test_crypto_ticker_timing(self):
        self._test_ticker_timing(self.crypto_ticker)

    def _test_ticker_timing(self, ticker: ticker.Ticker):
        ticker.wait_time = 5
        times = []
        for i, _ in enumerate(ticker.tick()):
            times.append(time.time())
            if i == 3:
                break
        # the time between iterations should roughly be the ticker wait_time
        assert np.mean(np.diff(times)) == pytest.approx(ticker.wait_time, abs=5)

    def test_crypto_no_api_key(self):
        with pytest.raises(ValueError):
            ticker.Ticker(symbol="BTC", symbol_type="crypto", api_key=None)


class TestSequence(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data_dir = Path(__file__).parents[1] / "data"
        cls.config_path = cls.data_dir / "config.json"
        cls.sequence = ticker.Sequence(
            [
                ticker.Ticker(
                    symbol="SPY",
                    symbol_type="stock",
                    api_key=None,
                    interval="1d",
                    lookback=30,
                ),
                ticker.Ticker(
                    symbol_type="crypto",
                    symbol="BTC",
                    api_key=API_KEY,
                    interval="1h",
                    lookback=24,
                ),
            ],
            skip_outdated=False,  # all data is outdated due to monkey patching
        )

    def test_sequence_from_tt_config(self):
        tt_config = config.TinytickerConfig.from_file(self.config_path)
        sequence = ticker.Sequence.from_tinyticker_config(tt_config)
        assert len(sequence.tickers) == len(tt_config.tickers)
        assert sequence.skip_empty is True
        assert sequence.skip_outdated is True

    def test_sequence_order(self):
        sequence = self.sequence
        # no wait time to speed up testing
        for ticker_ in sequence.tickers:
            ticker_.wait_time = 0
        for i, (ticker_, _) in enumerate(self.sequence.start()):
            assert ticker_.symbol == sequence.tickers[i % 2].symbol
            if i == 5:
                break
