import logging
import time
from datetime import datetime
from typing import Callable, Iterator, Optional

import pandas as pd
import cryptocompare
import yfinance

INTERVAL_LOOKBACKS = {
    "day": 30,
    "hour": 24,
    "minute": 30,
}
INTERVAL_WAIT_TIMES = {
    "day": 60 * 60 * 24,
    "hour": 60 * 60,
    "minute": 60,
}
INTERVAL_YFINANCE_FORMAT = {
    "day": "1d",
    "hour": "1h",
    "minute": "1m",
}
SYMBOL_TYPES = ["crypto", "stock"]


class Ticker:
    """Query the CryptoCompare API.

    Args:
        symbol_type: Either "crypto" or "stock".
        api_key: CryptoCompare API key, https://min-api.cryptocompare.com/pricing,
            required for obtaining crypto prices.
        symbol:  Ticker symbol, "AAPL", "BTC", "ETH", "DOGE" ...
        currency: Currency code for cryto, "USD", "EUR" ...
        interval: Candle interval, either "day", "hour" or "minute".
        lookback: How many intervals to look back.
        wait_time: Time to wait in between API calls.
    """

    def __init__(
        self,
        symbol_type: str = "crypto",
        api_key: Optional[str] = None,
        symbol: str = "BTC",
        currency: str = "USD",
        interval: str = "hour",
        lookback: Optional[int] = None,
        wait_time: Optional[int] = None,
    ) -> None:
        self._log = logging.getLogger(__name__)
        if symbol_type not in SYMBOL_TYPES:
            raise ValueError(f"'symbol_type' not in {SYMBOL_TYPES}")
        self.symbol_type = symbol_type
        self.interval = interval
        self._crypto_api_method = self.get_crypto_api_method()
        if interval not in INTERVAL_LOOKBACKS.keys():
            raise ValueError(f"'interval' not in {list(INTERVAL_LOOKBACKS.keys())}.")
        if self.symbol_type == "crypto" and api_key is None:
            raise ValueError("No API key provided.")
        self.api_key = api_key
        cryptocompare.cryptocompare._set_api_key_parameter(self.api_key)
        self.symbol = symbol
        self.currency = currency
        if lookback is None:
            self.lookback = INTERVAL_LOOKBACKS[self.interval]
        else:
            self.lookback = lookback  # type: int
        if wait_time is None:
            self.wait_time = INTERVAL_WAIT_TIMES[self.interval]
        else:
            self.wait_time = wait_time  # type: int

    def get_crypto_api_method(self) -> Callable:
        """Get the right method for the requested inverval.

        Returns:
            Appropriate API method.
        """
        return getattr(cryptocompare, "get_historical_price_" + self.interval)

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
                limit=self.lookback - 1,
            )
        )
        historical.set_index("time", inplace=True)
        historical.index = pd.to_datetime(historical.index, unit="s")  # type: ignore
        historical.rename(
            columns={"high": "High", "close": "Close", "low": "Low", "open": "Open"},
            inplace=True,
        )
        current = cryptocompare.get_price(self.symbol, self.currency)
        if current is not None:
            current = current[self.symbol][self.currency]

        return {"historical": historical, "current_price": current}

    def _tick_stock(self) -> dict:
        interval = INTERVAL_YFINANCE_FORMAT[self.interval]
        end = pd.to_datetime("now")
        delta = pd.Timedelta(interval)
        if delta == pd.NaT:
            raise ValueError("delta is NaT.")
        start = end - delta * (self.lookback - 1)  # type: ignore
        return {
            "historical": yfinance.download(
                self.symbol, start=start, end=end, interval=interval
            ),
            "current_price": None,
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
