import logging
import time
from datetime import datetime
from typing import Callable, Dict, Iterator, List, Optional, Tuple

import cryptocompare
import pandas as pd
import yfinance

CRYPTO_MAX_LOOKBACK = 1440
CRYPTO_CURRENCY = "USD"
SYMBOL_TYPES = ["crypto", "stock"]

YFINANCE_NON_STANDARD_INTERVALS = {
    "1wk": pd.to_timedelta("7d"),
    "1mo": pd.to_timedelta("30d"),
    "3mo": pd.to_timedelta("90d"),
}

INTERVAL_TIMEDELTAS = {
    interval: YFINANCE_NON_STANDARD_INTERVALS[interval]
    if interval in YFINANCE_NON_STANDARD_INTERVALS
    else pd.to_timedelta(interval)
    for interval in [
        "1m",
        "2m",
        "5m",
        "15m",
        "30m",
        "90m",
        "1h",
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
    "90m": 24,  # 36h
    "1h": 24,  # 24h
    "1d": 30,  # 1mo
    "5d": 30,  # 150d
    "1wk": 26,  # 6mo
    "1mo": 24,  # 2yrs
    "3mo": 24,  # 6 yrs
}

CRYPTO_INTERVAL_TIMEDELTAS = {
    "minute": pd.to_timedelta("1m"),
    "hour": pd.to_timedelta("1h"),
    "day": pd.to_timedelta("1d"),
}


LOGGER = logging.getLogger(__name__)


def get_cryptocompare(
    coin: str,
    interval_dt: pd.Timedelta,
    lookback: int,
) -> pd.DataFrame:
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
    historical = pd.DataFrame(
        api_method(
            coin,
            CRYPTO_CURRENCY,
            toTs=datetime.now(),
            limit=crypto_limit,
        )
    )
    LOGGER.debug("crypto historical data columns: %s", historical.columns)
    historical.set_index("time", inplace=True)
    historical.index = pd.to_datetime(historical.index, unit="s")  # type: ignore
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
        historical = historical.resample(interval_dt).agg(
            {
                "Open": "first",
                "High": "max",
                "Low": "min",
                "Close": "last",
                "Volume": "sum",
            }
        )
        historical.index = historical_index[::scale_factor]
    LOGGER.debug("crypto historical length: %s", len(historical))
    if len(historical) > lookback:
        historical = historical.iloc[len(historical) - lookback :]
    LOGGER.debug("crypto historical length pruned: %s", len(historical))
    return historical  # type: ignore


class Ticker:
    """Price data fetcher.

    Args:
        symbol_type: Either "crypto" or "stock".
        api_key: CryptoCompare API key, https://min-api.cryptocompare.com/pricing,
            required for obtaining crypto prices.
        symbol:  Ticker symbol, "AAPL", "BTC", "ETH", "DOGE" ...
        interval: Data time interval,
        lookback: How many intervals to look back.
        wait_time: Time to wait in between API calls.
        **kwargs: Extra args are provided to the `Display.plot` method.
    """

    def __init__(
        self,
        symbol_type: str = "crypto",
        api_key: Optional[str] = None,
        symbol: str = "BTC",
        interval: str = "1d",
        lookback: Optional[int] = None,
        wait_time: Optional[int] = None,
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
        self._display_kwargs = kwargs

    @property
    def single_tick(self) -> Callable:
        """Perform a single tick."""
        return self._symbol_type_map[self.symbol_type]

    def _tick_crypto(self) -> dict:
        """Query the crypto API.

        Returns:
            Dictionary containing the cryptocompare API's historical and current price data.
        """
        self._log.info("Crypto tick.")
        historical = get_cryptocompare(self.symbol, self._interval_dt, self.lookback)
        current = cryptocompare.get_price(self.symbol, CRYPTO_CURRENCY)
        if current is not None:
            current = current[self.symbol][CRYPTO_CURRENCY]

        return {"historical": historical, "current_price": current}

    def _tick_stock(self) -> dict:
        self._log.info("Stock tick.")
        end = pd.to_datetime("now")
        start = end - self._interval_dt * (self.lookback - 1)
        self._log.debug("interval: %s", self.interval)
        self._log.debug("self.lookback: %s", self.lookback)
        self._log.debug("start: %s", start)
        self._log.debug("end: %s", end)
        current_price_data = yfinance.download(
            self.symbol,
            start=end - pd.to_timedelta("2m"),
            end=end,
            interval="1m",
        )  # type: pd.DataFrame
        if current_price_data.empty:
            self._log.debug("current price data empty")
            current_price = None
        else:
            self._log.debug("current price data not empty")
            current_price = current_price_data.iloc[-1]["Close"]

        return {
            "historical": yfinance.download(
                self.symbol, start=start, end=end, interval=self.interval
            ),
            "current_price": current_price,
        }

    def tick(self) -> Iterator[dict]:
        """Tick forever.

        Returns:
            Iterator over the price data.
        """
        while True:
            self._log.info("Ticker start.")
            yield self.single_tick()
            self._log.debug("Sleeping %i s", self.wait_time)
            time.sleep(self.wait_time)

    def __str__(self) -> str:
        return f"Ticker\t{self.symbol_type}\t{self.symbol}\t{self.lookback}x{self.interval}\t{self.wait_time}s"


class Sequence:
    def __init__(self, tickers: List[Ticker]):
        """Runs multiple tickers."""
        if len(tickers) == 0:
            raise ValueError("No tickers provided.")
        self.tickers = tickers

    def start(self) -> Iterator[Tuple[Ticker, dict]]:
        while True:
            for ticker in self.tickers:
                yield (ticker, ticker.single_tick())
                time.sleep(ticker.wait_time)

    def __str__(self):
        return "Sequence \n" + "\n".join([ticker.__str__() for ticker in self.tickers])
