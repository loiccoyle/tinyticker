import time
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import pytest
import pytz

from tinyticker.tickers._base import TickerBase


def assert_tick_expected(
    ticker: TickerBase,
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
        assert (
            ticker.config.wait_time
            == pd.to_timedelta(ticker.config.interval).total_seconds()
        )
        assert resp.historical.index.tzinfo == pytz.UTC  # type: ignore
        assert (resp.historical.index == expected.index).all()
        assert (resp.historical.columns == expected.columns).all()


def assert_tick_timing(ticker: TickerBase):
    times = []
    for i, _ in enumerate(ticker.tick()):
        times.append(time.time())
        if i == 3:
            break
    # the time between iterations should roughly be the ticker wait_time
    assert np.mean(np.diff(times)) == pytest.approx(ticker.config.wait_time, abs=5)


def same(df1: pd.DataFrame, df2: pd.DataFrame) -> bool:
    return np.allclose(df1.to_numpy(), df2.to_numpy())


def assert_same_tick(ticker: TickerBase):
    # these two should return the same data because we monkey patched
    resp = ticker.single_tick()
    gen = ticker.tick()
    tick = next(gen)
    # assert resp.current_price == tick.current_price
    assert (resp.historical.index == tick.historical.index).all()
    assert same(resp.historical, tick.historical)
