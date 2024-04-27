import dataclasses as dc
import logging
import time
from typing import Callable, Dict, Iterator, List, Optional, Tuple

import cryptocompare
import pandas as pd
import yfinance

from . import utils
from .config import TinytickerConfig

CRYPTO_MAX_LOOKBACK = 1440
CRYPTO_CURRENCY = "USD"
SYMBOL_TYPES = ["crypto", "stock"]

YFINANCE_NON_STANDARD_INTERVALS: Dict[str, pd.Timedelta] = {
    "1wk": pd.to_timedelta("1W"),
    "1mo": pd.to_timedelta("30d"),
    "3mo": pd.to_timedelta("90d"),
}

INTERVAL_TIMEDELTAS: Dict[str, pd.Timedelta] = {
    interval: YFINANCE_NON_STANDARD_INTERVALS[interval]
    if interval in YFINANCE_NON_STANDARD_INTERVALS
    else pd.to_timedelta(interval)
    for interval in [
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
        "3mo",
    ]
}

INTERVAL_LOOKBACKS = {
    "1m": 20,  # 20m
    "2m": 15,  # 30m
    "5m": 24,  # 2h
    "15m": 16,  # 8h
    "30m": 24,  # 12h
    "1h": 24,  # 24h
    "90m": 24,  # 36h
    "1d": 30,  # 1mo
    "5d": 30,  # 150d
    "1wk": 26,  # 6mo
    "1mo": 24,  # 2yrs
    "3mo": 24,  # 6 yrs
}

CRYPTO_INTERVAL_TIMEDELTAS: Dict[str, pd.Timedelta] = {
    "minute": pd.to_timedelta("1m"),
    "hour": pd.to_timedelta("1h"),
    "day": pd.to_timedelta("1d"),
}

LOGGER = logging.getLogger(__name__)


@dc.dataclass
class Response:
    """The api response. Holds the historical and current price data.

    Args:
        historical: DataFrame with columns "Open", "Close", "High", "Low", "Volume"
            and a time index.
        current_price: The current price of the asset.
    """

    historical: pd.DataFrame
    current_price: float


def get_cryptocompare(
    token: str,
    interval_dt: pd.Timedelta,
    lookback: int,
) -> pd.DataFrame:
    """Wraps the crypto data API to have the same interface as the stock API.

    This involves working around `cryptocompare`'s 'limited interval choice by
    requesting more data and resampling ourselves. It also renames the columns and sets
    a time index.

    Args:
        token: token identifier e.g. BTC, ETH, ...
        interval_dt: the desired interval duration.
        lookback: how many intervals to fetch data for.

    Returns:
        A `pd.DataFrame` containing the Open, Close, High, Low and Volume historical
            data, with a time index.
    """

    max_timedelta = pd.Timedelta(0)
    crypto_interval = "minute"
    # get the biggest interval_dt which is smaller than the desired interval
    for interval, timedelta in CRYPTO_INTERVAL_TIMEDELTAS.items():
        if max_timedelta <= timedelta <= interval_dt:
            max_timedelta = timedelta
            crypto_interval = interval
    crypto_interval_dt = CRYPTO_INTERVAL_TIMEDELTAS[crypto_interval]
    # how much to extend the query back in time so that after resampling
    # we get the correct lookback
    scale_factor = int(interval_dt / crypto_interval_dt)
    api_method = getattr(cryptocompare, "get_historical_price_" + crypto_interval)
    crypto_limit = min(
        lookback * scale_factor,
        CRYPTO_MAX_LOOKBACK,
    )
    historical: pd.DataFrame = pd.DataFrame(
        api_method(
            token,
            CRYPTO_CURRENCY,
            toTs=utils.now().timestamp(),
            limit=crypto_limit,
        )
    )
    LOGGER.debug("crypto historical data columns: %s", historical.columns)
    historical.set_index("time", inplace=True)
    historical.index = pd.to_datetime(historical.index.to_numpy(), unit="s", utc=True)
    historical.drop(
        columns=["volumeto", "conversionType", "conversionSymbol"],
        inplace=True,
    )
    historical.rename(
        columns={
            "high": "High",
            "close": "Close",
            "low": "Low",
            "open": "Open",
            "volumefrom": "Volume",
        },
        inplace=True,
    )
    if crypto_interval_dt != interval_dt:
        LOGGER.debug("resampling historical data")
        # resample the crypto data to get the desired interval
        historical_index = historical.index
        historical: pd.DataFrame = historical.resample(interval_dt).agg(
            {
                "Open": "first",
                "High": "max",
                "Low": "min",
                "Close": "last",
                "Volume": "sum",
            }
        )  # type: ignore
        historical.index = historical_index[::scale_factor]
    LOGGER.debug("crypto historical length: %s", len(historical))
    if len(historical) > lookback:
        historical = historical.iloc[-lookback:]
    LOGGER.debug("crypto historical length pruned: %s", len(historical))
    return historical


class Ticker:
    """Price data fetcher.

    Args:
        api_key: CryptoCompare API key, https://min-api.cryptocompare.com/pricing,
            required for fetching crypto prices.
        symbol_type: Either "crypto" or "stock".
        symbol:  Ticker or token identifier, "AAPL", "BTC", "ETH", "DOGE" ...
        interval: Data time interval.
        lookback: How many intervals to look back.
        wait_time: Time to wait in between API calls.
        avg_buy_price: Average buy price of the asset.
        **kwargs: Extra args are provided to the `Display.plot` method.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        symbol_type: str = "crypto",
        symbol: str = "BTC",
        interval: str = "1d",
        lookback: Optional[int] = None,
        wait_time: Optional[int] = None,
        avg_buy_price: Optional[float] = None,
        **kwargs,
    ) -> None:
        self._log = logging.getLogger(__name__)
        if symbol_type not in SYMBOL_TYPES:
            raise ValueError(f"'symbol_type' not in {SYMBOL_TYPES}")
        self.symbol_type = symbol_type
        if interval not in INTERVAL_TIMEDELTAS.keys():
            raise ValueError(f"'interval' not in {INTERVAL_TIMEDELTAS.keys()}")
        self.interval = interval
        self._log.debug("interval: %s", self.interval)
        self._interval_dt = INTERVAL_TIMEDELTAS[self.interval]
        if self._interval_dt == pd.NaT:
            raise ValueError("interval Timedelta is NaT.")
        if self.symbol_type == "crypto" and api_key is None:
            raise ValueError("No API key provided.")
        self.api_key = api_key
        if self.api_key is not None:
            cryptocompare.cryptocompare._set_api_key_parameter(self.api_key)
        self.symbol = symbol
        if lookback is None:
            self._log.debug("lookback None")
            self.lookback = INTERVAL_LOOKBACKS[self.interval]
        else:
            self._log.debug("lookback not None")
            self.lookback = lookback  # type: int
        self._log.debug("lookback: %s", self.lookback)
        if wait_time is None:
            self.wait_time = int(self._interval_dt.value * 1e-9)
        else:
            self.wait_time = wait_time  # type: int
        self._log.debug("wait_time: %s", self.wait_time)
        self._symbol_type_map: Dict[str, Callable] = {
            "crypto": self._tick_crypto,
            "stock": self._tick_stock,
        }
        self.avg_buy_price = avg_buy_price
        self._display_kwargs = kwargs

    @property
    def single_tick(self) -> Callable[[], Response]:
        """Perform a single tick.

        Returns:
            The response from the API.
        """
        return self._symbol_type_map[self.symbol_type]

    def _current_price_fallback(
        self, historical: pd.DataFrame, current_price: Optional[float]
    ) -> Response:
        return Response(
            historical,
            historical.iloc[-1]["Close"] if current_price is None else current_price,
        )

    def _tick_crypto(self) -> Response:
        """Query the crypto API.

        Returns:
            The response from the API.
        """
        self._log.info("Crypto tick.")
        historical = get_cryptocompare(self.symbol, self._interval_dt, self.lookback)
        current = cryptocompare.get_price(self.symbol, CRYPTO_CURRENCY)
        if current is not None:
            current_price = current[self.symbol][CRYPTO_CURRENCY]
        else:
            current_price = None

        return self._current_price_fallback(historical, current_price)

    def _get_yfinance_start_end(self) -> Tuple[pd.Timestamp, pd.Timestamp]:
        end = utils.now()
        # depending on the interval we need to increase the time range to compensate for the market
        # being closed
        start = end - self._interval_dt * self.lookback
        if self._interval_dt < pd.to_timedelta("1d"):
            # to compensate for the market being closed
            # US market is open 6.5h a day, probably roughly the same for other markets
            n_trade_days = (
                self._interval_dt * self.lookback // pd.to_timedelta("6.5h") + 1
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

    def _tick_stock(
        self,
    ) -> Response:
        """Query the stock API.

        Returns:
            The response from the API.
        """
        self._log.info("Stock tick.")
        start, end = self._get_yfinance_start_end()
        self._log.debug("interval: %s", self.interval)
        self._log.debug("lookback: %s", self.lookback)
        self._log.debug("start: %s", start)
        self._log.debug("end: %s", end)
        current_price_data: pd.DataFrame = yfinance.download(
            self.symbol,
            start=end - pd.to_timedelta("2m"),
            end=end,
            interval="1m",
        )
        historical: pd.DataFrame = yfinance.download(
            self.symbol,
            start=start,
            end=end,
            interval=self.interval,
            timeout=None,  # type: ignore
        )
        if historical.empty:
            raise ValueError("No historical data returned from yfinance API.")
        if not current_price_data.empty:
            current_price = current_price_data.iloc[-1]["Close"]
        else:
            current_price = None
        # drop the extra data
        if len(historical) > self.lookback:
            historical = historical.iloc[-self.lookback :]
        if historical.index.tzinfo is None:  # type: ignore
            historical.index = historical.index.tz_localize("utc")  # type: ignore
        return self._current_price_fallback(historical, current_price)

    def tick(self) -> Iterator[Response]:
        """Tick forever.

        Returns:
            Iterator over the API responses.
        """
        while True:
            self._log.info("Ticker start.")
            yield self.single_tick()
            self._log.debug("Sleeping %i s", self.wait_time)
            time.sleep(self.wait_time)

    def __str__(self) -> str:
        return "\t".join(
            [
                "Ticker",
                self.symbol_type,
                self.symbol,
                f"{self.lookback}x{self.interval}",
                str(self.wait_time),
            ]
        )


class Sequence:
    @classmethod
    def from_tinyticker_config(cls, tt_config: TinytickerConfig) -> "Sequence":
        """Create a `Sequence` from a `TinytickerConfig`.

        Args:
            tt_config: `TinytickerConfig` from which to create the `Sequence`.

        Returns:
            The `Sequence` instance.
        """
        return Sequence(
            [
                Ticker(
                    api_key=tt_config.api_key,
                    symbol_type=ticker.symbol_type,
                    symbol=ticker.symbol,
                    interval=ticker.interval,
                    lookback=ticker.lookback,
                    wait_time=ticker.wait_time,
                    plot_type=ticker.plot_type,
                    mav=ticker.mav,
                    volume=ticker.volume,
                    avg_buy_price=ticker.avg_buy_price,
                )
                for ticker in tt_config.tickers
            ],
            skip_empty=tt_config.sequence.skip_empty,
            skip_outdated=tt_config.sequence.skip_outdated,
        )

    def __init__(
        self,
        tickers: List[Ticker],
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

    def start(self) -> Iterator[Tuple[Ticker, Response]]:
        """Start iterating through the tickers.

        Returns:
            The `Ticker` instance and the response from the API.
        """
        # if all tickers are skipped, we want to sleep a bit
        all_skipped_cooldown = 300  # 5min

        all_skipped = False
        while True:
            if all_skipped:
                LOGGER.info(f"All tickers skipped, sleeping {all_skipped_cooldown}s.")
                time.sleep(all_skipped_cooldown)
            all_skipped = True
            for ticker in self.tickers:
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
                    outdated_min_delta = max(pd.to_timedelta("5m"), ticker._interval_dt)
                    # when fetching daily data from yfinance, the timestamps are 00:00:00 of the day in question
                    # which covers the full day's trade from open to close, so we relax the outdated constraint.
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
                time.sleep(ticker.wait_time)

    def __str__(self):
        return (
            f"Sequence(skip_outdated={self.skip_outdated}, skip_empty={self.skip_empty}): \n"
            + "\n".join([ticker.__str__() for ticker in self.tickers])
        )
