import logging
import time
from datetime import datetime
from typing import Callable, Iterator, Optional

import pandas as pd
import numpy as np
import cryptocompare
import yfinance

CRYPTO_MAX_LOOKBACK = 1440
SYMBOL_TYPES = ["crypto", "stock"]

YFINANCE_NON_STANDARD_INTERVALS = {
    "1wk": pd.Timedelta("7d"),
    "1mo": pd.Timedelta("30d"),
    "3mo": pd.Timedelta("90d"),
}

INTERVAL_TIMEDELTAS = {
    interval: YFINANCE_NON_STANDARD_INTERVALS[interval]
    if interval in YFINANCE_NON_STANDARD_INTERVALS
    else pd.Timedelta(interval)
    for interval in [
        "1m",
        "2m",
        "5m",
        "15m",
        "30m",
        "60m",
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
    "60m": 24,  # 24h
    "90m": 24,  # 36h
    "1h": 24,  # 24h
    "1d": 30,  # 1mo
    "5d": 30,  # 150d
    "1wk": 26,  # 6mo
    "1mo": 24,  # 2yrs
    "3mo": 24,  # 6 yrs
}

CRYPTO_INTERVAL_TIMEDELTAS = {
    "minute": pd.Timedelta("1m"),
    "hour": pd.Timedelta("1h"),
    "day": pd.Timedelta("1d"),
}


class Ticker:
    """Query the CryptoCompare API.

    Args:
        symbol_type: Either "crypto" or "stock".
        api_key: CryptoCompare API key, https://min-api.cryptocompare.com/pricing,
            required for obtaining crypto prices.
        symbol:  Ticker symbol, "AAPL", "BTC", "ETH", "DOGE" ...
        currency: Currency code for cryto, "USD", "EUR" ...
        interval: Data time interval,
        lookback: How many intervals to look back.
        wait_time: Time to wait in between API calls.
    """

    def __init__(
        self,
        symbol_type: str = "crypto",
        api_key: Optional[str] = None,
        symbol: str = "BTC",
        currency: str = "USD",
        interval: str = "1d",
        lookback: Optional[int] = None,
        wait_time: Optional[int] = None,
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
        cryptocompare.cryptocompare._set_api_key_parameter(self.api_key)
        self.symbol = symbol
        self.currency = currency
        if lookback is None:
            self._log.debug("lookback None")
            self.lookback = INTERVAL_LOOKBACKS[self.interval]
        else:
            self._log.debug("lookback not None")
            self.lookback = lookback  # type: int
        self._log.debug("lookback: %s", self.lookback)
        if wait_time is None:
            self.wait_time = self._interval_dt.value * 1e-9  # type: ignore
        else:
            self.wait_time = wait_time  # type: int
        self._log.debug("wait_time: %s", self.wait_time)

        self._crypto_interval = self._get_crypto_interval()
        self._crypto_interval_dt = CRYPTO_INTERVAL_TIMEDELTAS[self._crypto_interval]
        self._crypto_scale_factor = int(self._interval_dt / self._crypto_interval_dt)
        self._crypto_api_method = self.get_crypto_api_method()
        self._crypto_lookback = self._get_crypto_lookback()



    def get_crypto_api_method(self) -> Callable:
        """Get the right method for the requested inverval.

        Returns:
            Appropriate API method.
        """
        return getattr(cryptocompare, "get_historical_price_" + self._crypto_interval)

    def _get_crypto_interval(self) -> str:
        max_timedelta = pd.Timedelta(0)
        out = "minute"
        for interval, timedelta in CRYPTO_INTERVAL_TIMEDELTAS.items():
            if timedelta <= self._interval_dt and timedelta >= max_timedelta:
                max_timedelta = timedelta
                out = interval
        self._log.debug("crypto_interval: %s", out)
        return out

    def _get_crypto_lookback(self) -> int:
        self._log.debug("crypto_interval_dt: %s", self._crypto_interval_dt)
        return min(
            self.lookback * self._crypto_scale_factor,  # type: ignore
            CRYPTO_MAX_LOOKBACK,
        )

    def _tick_crypto(self) -> dict:
        """Query the crypto API.

        Returns:
            Iterator which returns the cryptocompare API's historical and current price data.
        """
        self._log.info("Crypto tick.")
        historical = pd.DataFrame(
            self._crypto_api_method(
                self.symbol,
                self.currency,
                toTs=datetime.now(),
                limit=self._crypto_lookback,
            )
        )
        historical.set_index("time", inplace=True)
        historical.index = pd.to_datetime(historical.index, unit="s")  # type: ignore
        historical.rename(
            columns={"high": "High", "close": "Close", "low": "Low", "open": "Open"},
            inplace=True,
        )
        if self._crypto_interval_dt != self._interval_dt:
            self._log.debug("Resampling crypto data.")
            # resample the crypto data to get the desired interval
            historical_index = historical.index
            historical = historical.groupby(
                np.arange(len(historical)) // self._crypto_scale_factor
            ).sum()
            historical.index = historical_index[::self._crypto_scale_factor]
            # drop the last candle because it hasn't finished
            historical = historical.iloc[:-1]
        else:
            historical = historical.iloc[1:]
        current = cryptocompare.get_price(self.symbol, self.currency)
        if current is not None:
            current = current[self.symbol][self.currency]

        return {"historical": historical, "current_price": current}

    def _tick_stock(self) -> dict:
        self._log.info("Stock tick.")
        end = pd.to_datetime("now")
        start = end - self._interval_dt * (self.lookback - 1)  # type: ignore
        self._log.debug("interval: %s", self.interval)
        self._log.debug("self.lookback: %s", self.lookback)
        self._log.debug("start: %s", start)
        self._log.debug("end: %s", end)
        current_price_data = yfinance.download(
            self.symbol,
            start=end - pd.Timedelta("2m"),  # type: ignore
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
        if self.symbol_type == "crypto":
            tick_method = self._tick_crypto
        elif self.symbol_type == "stock":
            tick_method = self._tick_stock
        else:
            raise ValueError(f"'symbol_type' not in {SYMBOL_TYPES}")

        while True:
            self._log.info("Ticker start.")
            yield tick_method()
            self._log.debug("Sleeping %i s", self.wait_time)
            time.sleep(self.wait_time)
