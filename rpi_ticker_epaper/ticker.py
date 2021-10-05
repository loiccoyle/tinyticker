import logging
import time
from datetime import datetime
from typing import Callable, Iterator, Optional, Union

import cryptocompare

INTERVAL_LOOKBACKS = {
    "day": 15,
    "hour": 12,
    "minute": 30,
}
INTERVAL_WAIT_TIMES = {
    "day": 60 * 60 * 24,
    "hour": 60 * 60,
    "minute": 60,
}


class Ticker:
    """Query the CryptoCompare API.

    Args:
        api_key: CryptoCompare API key, https://min-api.cryptocompare.com/pricing.
        coin: Crypto coin, "BTC", "ETH", "DOGE" ...
        currency: Currency code, "USD", "EUR" ...
        interval: Candle interval, either "day", "hour" or "minute".
        look_back: How many intervals to look back.
        wait_time: Time to wait in between API calls.
    """

    def __init__(
        self,
        api_key: str,
        coin: str = "BTC",
        currency: str = "USD",
        interval: str = "hour",
        look_back: Optional[int] = None,
        wait_time: Optional[int] = None,
    ) -> None:
        self._log = logging.getLogger(__name__)
        self.interval = interval
        self.api_method = self.get_api_method()
        if interval not in INTERVAL_LOOKBACKS.keys():
            raise ValueError(f"'interval' not in {list(INTERVAL_LOOKBACKS.keys())}.")
        self.api_key = api_key
        cryptocompare.cryptocompare._set_api_key_parameter(self.api_key)
        self.coin = coin
        self.currency = currency
        if look_back is None:
            self.look_back = INTERVAL_LOOKBACKS[self.interval]
        else:
            self.look_back = look_back  # type: int
        if wait_time is None:
            self.wait_time = INTERVAL_WAIT_TIMES[self.interval]
        else:
            self.wait_time = wait_time  # type: int

    def get_api_method(self) -> Callable:
        return getattr(cryptocompare, "get_historical_price_" + self.interval)

    def tick(self) -> Iterator[Union[dict, None]]:
        """Perform the queries and yield the responses forever.

        Returns:
            Iterator which returns the API responses.
        """
        self._log.info("Started ticking.")
        while True:
            try:
                yield self.api_method(
                    self.coin,
                    self.currency,
                    toTs=datetime.now(),
                    limit=self.look_back - 1,
                )
            except Exception:
                yield None
            self._log.debug("Sleeping %i s", self.wait_time)
            time.sleep(self.wait_time)
