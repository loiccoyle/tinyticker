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

    def _single_tick(self) -> Tuple[pd.DataFrame, Optional[float]]:
        LOGGER.info("Stock tick: %s", self.config.symbol)
        start, end = self._get_yfinance_start_end()
        current_price_data: pd.DataFrame = yfinance.download(
            self.config.symbol,
            start=end - pd.to_timedelta("2m"),
            end=end,
            interval="1m",
            prepost=self.config.prepost,
            progress=False,
        )
        historical: pd.DataFrame = yfinance.download(
            self.config.symbol,
            start=start,
            end=end,
            interval=self.config.interval,
            timeout=None,  # type: ignore
            prepost=self.config.prepost,
            progress=False,
        )
        if historical.empty:
            raise ValueError(
                f"No historical data returned from yfinance API for {self.config.symbol}."
            )
        if not current_price_data.empty:
            current_price = current_price_data.iloc[-1]["Close"]
        else:
            current_price = None
        # drop the extra data
        if len(historical) > self.lookback:
            historical = historical.iloc[-self.lookback :]
        if historical.index.tzinfo is None:  # type: ignore
            historical.index = historical.index.tz_localize("utc")  # type: ignore
        return (historical, current_price)
