import dataclasses as dc
import logging
import time
from typing import Dict, Iterator, Literal, Optional, Tuple, Union

import pandas as pd
from PIL.Image import Image

from ..config import TickerConfig, TinytickerConfig

LOGGER = logging.getLogger(__name__)

INTERVALS = [
    "1m",
    "2m",
    "5m",
    "15m",
    "30m",
    "1h",
    "90m",
    "1d",
    "5d",
    "1wk",
    "1mo",
]

# pd.to_timedelta does not support these strings
WEIRD_INTERVALS: Dict[str, pd.Timedelta] = {
    "1wk": pd.to_timedelta("1W"),
    "1mo": pd.to_timedelta("30d"),
}

INTERVAL_TIMEDELTAS: Dict[str, pd.Timedelta] = {
    interval: WEIRD_INTERVALS[interval]
    if interval in WEIRD_INTERVALS
    else pd.to_timedelta(interval)
    for interval in INTERVALS
}

INTERVAL_LOOKBACKS = {
    "1m": 20,  # 20m
    "2m": 30,  # 1h
    "5m": 24,  # 2h
    "15m": 32,  # 16h
    "30m": 24,  # 12h
    "1h": 24,  # 24h
    "90m": 24,  # 36h
    "1d": 30,  # 1mo
    "5d": 30,  # 150d
    "1wk": 26,  # 6mo
    "1mo": 24,  # 2yrs
    "3mo": 24,  # 6 yrs
}


@dc.dataclass
class TickerResponse:
    """The api response. Holds the historical and current price data.

    Args:
        historical: DataFrame with columns "Open", "Close", "High", "Low", "Volume"
            and a time index.
        current_price: The current price of the asset.
    """

    historical: pd.DataFrame
    current_price: float


class TickerBase:
    currency: str

    @classmethod
    def from_config(
        cls, tt_config: TinytickerConfig, ticker_config: TickerConfig
    ) -> "TickerBase":
        """Create a Ticker instance from a `TinytickerConfig` and `TickerConfig`."""
        ...

    def __init__(self, config: TickerConfig) -> None:
        self._logo = None
        self.config = config
        self.interval_dt = INTERVAL_TIMEDELTAS[config.interval]
        self.lookback = (
            self.config.lookback
            if self.config.lookback is not None
            else INTERVAL_LOOKBACKS[config.interval]
        )

    @property
    def logo(self) -> Union[Image, Literal[False]]:
        if self._logo is None:
            LOGGER.debug("Fetching logo")
            self._logo = self._get_logo()
        return self._logo  # type: ignore

    def _get_logo(self) -> Union[Image, Literal[False]]:
        """Get the logo, should return false if it couldn't be fetched."""
        ...

    def _single_tick(self) -> Tuple[pd.DataFrame, Optional[float]]: ...

    def single_tick(self) -> TickerResponse:
        """Get the historical and current price data for a single tick.

        Returns:
            The `Response` object.
        """
        return self._current_price_fallback(*self._single_tick())

    def _current_price_fallback(
        self, historical: pd.DataFrame, current_price: Optional[float]
    ) -> TickerResponse:
        """Fallback to the last historical close price if the current price is not available.

        Args:
            historical: The historical price data.
            current_price: The current price.

        Returns:
            The response object.
        """
        return TickerResponse(
            historical,
            historical.iloc[-1]["Close"] if current_price is None else current_price,
        )

    def tick(self) -> Iterator[TickerResponse]:
        """Tick forever.

        Returns:
            Iterator over the responses.
        """
        while True:
            LOGGER.info("Ticker start.")
            yield self.single_tick()
            LOGGER.debug("Sleeping %i s", self.config.wait_time)
            time.sleep(self.config.wait_time)

    def __str__(self) -> str:
        return "\t".join(
            [
                "Ticker",
                self.config.symbol_type,
                self.config.symbol,
                f"{self.lookback}x{self.config.interval}",
                f"{self.config.wait_time}s",
            ]
        )
