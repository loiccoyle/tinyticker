import logging
import time
from typing import Iterator, List, Union

import cryptocompare


class Ticker:
    """Query the CryptoCompare API.

    Args:
        api_key: CryptoCompare API key, https://min-api.cryptocompare.com/pricing.
        wait_time: Number of seconds between API queries.
    """

    def __init__(self, api_key: str, wait_time: int = 120) -> None:
        self._log = logging.getLogger(__name__)
        self.wait_time = wait_time
        self.api_key = api_key
        cryptocompare.cryptocompare._set_api_key_parameter(self.api_key)

    def tick(
        self,
        coins: Union[str, List[str]] = ["BTC", "ETH"],
        currencies: Union[str, List[str]] = "USD",
        **kwargs
    ) -> Iterator[Union[dict, None]]:
        """Perform the queries and yield the responses forever.

        Args:
            coins: crypto coins to query the price of.
            currencies: currencies in which to display the prices.
            **kwargs: passed to `cryptocompare.get_price`.

        Returns:
            Iterator which returns the API responses.
        """
        self._log.info("Started ticking.")
        while True:
            try:
                yield cryptocompare.get_price(coins, currencies, **kwargs)  # type: ignore
            except Exception:
                yield None
            self._log.debug("Sleeping %i s", self.wait_time)
            time.sleep(self.wait_time)
