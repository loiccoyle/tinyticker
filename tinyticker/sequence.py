import asyncio
import logging
import time
from typing import AsyncGenerator, List, Optional, Tuple

import pandas as pd

from . import utils
from .config import TinytickerConfig
from .tickers import Ticker
from .tickers._base import TickerBase, TickerResponse

LOGGER = logging.getLogger(__name__)


class Sequence:
    @classmethod
    def from_tinyticker_config(cls, tt_config: TinytickerConfig) -> "Sequence":
        """Create a `Sequence` from a `TinytickerConfig`.

        Args:
            tt_config: `TinytickerConfig` from which to create the `Sequence`.

        Returns:
            The `Sequence` instance.
        """
        tickers = []
        for ticker_config in tt_config.tickers:
            try:
                tickers.append(Ticker(tt_config=tt_config, ticker_config=ticker_config))
            except Exception as e:
                LOGGER.error(f"Failed to create ticker: {e}")
                continue

        return Sequence(
            tickers,
            skip_empty=tt_config.sequence.skip_empty,
            skip_outdated=tt_config.sequence.skip_outdated,
        )

    def __init__(
        self,
        tickers: List[TickerBase],
        skip_empty: bool = True,
        skip_outdated: bool = True,
    ):
        """Runs multiple `Ticker` instances in sequence.

        Args:
            tickers: list of `Ticker` instances.
            skip_empty: if the response doesn't contain any data, move on to the next ticker.
            skip_outdated: if the last candle of the response is too old, move on to the next
                ticker. This typically happens when the stock market closes.
        """
        if len(tickers) == 0:
            raise ValueError("No tickers provided.")
        self.tickers = tickers
        self.skip_empty = skip_empty
        self.skip_outdated = skip_outdated

        self.current_index: Optional[int] = None
        self._skip_ticker = False
        self._got_to_index: Optional[int] = None

    def go_to_index(self, index: int) -> None:
        """Skip to a specific ticker.
        Args:
            index: index of the ticker to skip to.
        """
        if index < 0 or index >= len(self.tickers):
            LOGGER.error(f"Invalid index {index}.")
            return
        self._skip_ticker = True
        self._go_to_index = index

    async def start(
        self,
    ) -> AsyncGenerator[Tuple[TickerBase, TickerResponse], None]:
        """Start iterating through the tickers.

        Returns:
            The `Ticker` instance and its response.
        """
        # if all tickers are skipped, we want to sleep for the smallest wait time
        all_skipped_cooldown = min(ticker.config.wait_time for ticker in self.tickers)

        all_skipped = False
        while True:
            if all_skipped:
                LOGGER.info(f"All tickers skipped, sleeping {all_skipped_cooldown}s.")
                time.sleep(all_skipped_cooldown)
            all_skipped = True
            for i, ticker in enumerate(self.tickers):
                if self._skip_ticker:
                    if self._go_to_index == i % len(self.tickers):
                        self._skip_ticker = False
                    else:
                        LOGGER.debug(f"Skipping {ticker}.")
                        continue
                self.current_index = i % len(self.tickers)

                try:
                    response = ticker.single_tick()
                except Exception as e:
                    LOGGER.error(f"{ticker} failed with {e}")
                    continue
                if self.skip_empty and (
                    response.historical is None or response.historical.empty
                ):
                    LOGGER.debug(f"{ticker} response empty, skipping.")
                    continue
                if self.skip_outdated:
                    # we want to skip the ticker if the last candle is too old, but because running
                    # this code takes some time, we relax the min constraint a bit.
                    outdated_min_delta = max(pd.to_timedelta("5m"), ticker.interval_dt)
                    # when fetching daily data from yfinance, the timestamps are 00:00:00
                    # of the day in question which covers the full day's trade from open
                    # to close, so we relax the outdated constraint.
                    if outdated_min_delta == pd.to_timedelta("1d"):
                        outdated_min_delta *= 2
                    if (
                        (utils.now() - response.historical.index[-1])  # type: ignore
                        > outdated_min_delta
                    ):
                        LOGGER.debug(f"{ticker} response outdated, skipping.")
                        continue
                all_skipped = False
                yield (ticker, response)

                LOGGER.info(f"Sleeping {ticker.config.wait_time}s.")
                # we want to sleep for the ticker's wait time and check every second if we
                # should skip this ticker.
                for _ in range(ticker.config.wait_time):
                    if self._skip_ticker:
                        LOGGER.info(f"Stop waiting, skipping {ticker}.")
                        break
                    await asyncio.sleep(1)

    def __str__(self):
        return (
            f"Sequence(skip_outdated={self.skip_outdated}, skip_empty={self.skip_empty}): \n"
            + "\n".join([ticker.__str__() for ticker in self.tickers])
        )
