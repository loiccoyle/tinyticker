import logging
from typing import Any, Dict, Optional, Tuple

import pandas as pd
import yahooquery as yq

from .. import utils
from ._base import TickerBase

LOGGER = logging.getLogger(__name__)


class TickerStock(TickerBase):
    @classmethod
    def from_config(cls, tt_config, ticker_config) -> "TickerStock":
        return TickerStock(ticker_config)

    def __init__(self, config) -> None:
        super().__init__(config)
        self._yq_ticker = yq.Ticker(self.config.symbol)
        price = self._yq_ticker.price[self.config.symbol]
        if isinstance(price, str):
            raise ValueError(price)
        self.currency = price["currency"]

    def current_price(self) -> float:
        price_data: Dict[str, Any] = self._yq_ticker.price[self.config.symbol]  # type: ignore
        market_state: str = price_data["marketState"]
        print(market_state)
        if (not self.config.prepost) or market_state == "REGULAR":
            return price_data["regularMarketPrice"]
        elif market_state == "PRE":
            return price_data["preMarketPrice"]
        else:
            # when the market is closed or postpost, we still want the latest price
            return price_data["postMarketPrice"]

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
        # add one more row before and after open/close to make sure we don't miss the start/end
        prepost_range |= prepost_range.shift(-1).fillna(False)
        prepost_range |= prepost_range.shift(1).fillna(False)
        # When in prepost, the high & lows can be off
        high_bars = historical["High"] - historical[["Close", "Open"]].max(axis=1)
        low_bars = historical[["Close", "Open"]].min(axis=1) - historical["Low"]

        to_correct_high = (
            high_bars[prepost_range]
            > high_bars[~prepost_range].mean() + high_bars[~prepost_range].std()
        )
        to_correct_low = (
            low_bars[prepost_range]
            > low_bars[~prepost_range].mean() + low_bars[~prepost_range].std()
        )
        # we could also set them to the avg of the previous and next high/low
        historical.loc[prepost_range & to_correct_high, "High"] = historical[
            ["Close", "Open"]
        ].max(axis=1)
        historical.loc[prepost_range & to_correct_low, "Low"] = historical[
            ["Close", "Open"]
        ].min(axis=1)

        self._log.debug("Fixed %s high values", to_correct_high.sum())
        self._log.debug("Fixed %s low values", to_correct_low.sum())
        return historical

    def _single_tick(self) -> Tuple[pd.DataFrame, Optional[float]]:
        LOGGER.info("Stock tick: %s", self.config.symbol)
        # clear the cached price data
        start, end = self._get_yfinance_start_end()
        historical = self._yq_ticker.history(
            start=start,
            end=end,
            interval=self.config.interval,
            prepost=self.config.prepost,
        ).droplevel("symbol")
        if historical.empty:
            raise ValueError(
                f"No historical data returned from yahoo finance API for {self.config.symbol}."
            )
        # drop the extra data
        if len(historical) > self.lookback:
            historical = historical.iloc[-self.lookback :]
        if not isinstance(historical.index, pd.DatetimeIndex):
            # depending on the the interval, the index returned by yq can be a DatetimeIndex or
            # an Index of strings
            historical.index = pd.to_datetime(historical.index)
        if historical.index.tz is None:
            historical.index = historical.index.tz_localize("utc")
        if self.config.prepost:
            # yfinance gives some weird data for the high/low values during the pre/post market
            # hours, so we hide them
            historical = self._fix_prepost(historical)
        return (historical, self.current_price())
