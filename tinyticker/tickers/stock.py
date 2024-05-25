import logging
from typing import Optional, Tuple

import pandas as pd
import yfinance

from .. import utils
from ._base import TickerBase

LOGGER = logging.getLogger(__name__)


class TickerStock(TickerBase):
    @classmethod
    def from_config(cls, tt_config, ticker_config) -> "TickerStock":
        return TickerStock(ticker_config)

    def __init__(self, config) -> None:
        super().__init__(config)
        self._yf_ticker = yfinance.Ticker(self.config.symbol)

    def _get_yfinance_start_end(self) -> Tuple[pd.Timestamp, pd.Timestamp]:
        end = utils.now()
        # depending on the interval we need to increase the time range to compensate for the market
        # being closed
        start = end - self.interval_dt * self.lookback
        if self.interval_dt < pd.to_timedelta("1d"):
            # to compensate for the market being closed
            # US market is open 6.5h a day, probably roughly the same for other markets
            n_trade_days = (
                self.interval_dt * self.lookback // pd.to_timedelta("6.5h") + 1
            )
            start -= pd.to_timedelta("1d") * n_trade_days
        # if we passed a weekend, add 2 days and a bit more because the added days can themselves
        # be weekends
        start -= pd.to_timedelta("2d") * (end.week - start.week) * 1.5
        # go back before weekend
        # start.weekday() returns 6 for Sunday, and 5 for Saturday
        # max(0, start.weekday() - 4) is 0 for Mon-Fri, 1 for Sat, 2 for Sun
        start -= pd.to_timedelta("1d") * max(0, start.weekday() - 4)
        return (start, end)

    def _fix_prepost(self, historical: pd.DataFrame) -> pd.DataFrame:
        # when the market is closed, the volume is 0
        prepost_range = historical["Volume"] == 0
        # When in prepost, the high & lows can be off
        to_correct_high = (
            historical["High"].diff()[prepost_range] > historical["High"].std()
        )
        to_correct_low = (
            historical["Low"].diff()[prepost_range]
            < historical["Low"].mean() - historical["Low"].std()
        )
        # we could also set them to the avg of the previous and next high/low
        historical.loc[prepost_range & to_correct_high, "High"] = historical["Close"]
        historical.loc[prepost_range & to_correct_low, "Low"] = historical["Close"]
        return historical

    def _single_tick(self) -> Tuple[pd.DataFrame, Optional[float]]:
        LOGGER.info("Stock tick: %s", self.config.symbol)
        start, end = self._get_yfinance_start_end()
        current_price: Optional[float] = self._yf_ticker.fast_info.get(
            "lastPrice", None
        )
        historical = self._yf_ticker.history(
            start=start,
            end=end,
            interval=self.config.interval,
            timeout=None,
            prepost=self.config.prepost,
        )
        if historical.empty:
            raise ValueError(
                f"No historical data returned from yfinance API for {self.config.symbol}."
            )
        # drop the extra data
        if len(historical) > self.lookback:
            historical = historical.iloc[-self.lookback :]
        if historical.index.tzinfo is None:  # type: ignore
            historical.index = historical.index.tz_localize("utc")  # type: ignore
        if self.config.prepost:
            # yfinance gives some weird data for the high/low values during the pre/post market
            # hours, so we hide very them
            historical = self._fix_prepost(historical)
        return (historical, current_price)
