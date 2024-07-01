import io
import logging
from typing import Dict, Optional, Tuple

import cryptocompare
import pandas as pd
import requests
from PIL import Image

from .. import utils
from ..config import TickerConfig
from ._base import TickerBase

CRYPTO_CURRENCY = "USD"
CRYPTO_MAX_LOOKBACK = 1440
CRYPTO_INTERVAL_TIMEDELTAS: Dict[str, pd.Timedelta] = {
    "minute": pd.to_timedelta("1m"),
    "hour": pd.to_timedelta("1h"),
    "day": pd.to_timedelta("1d"),
}

LOGGER = logging.getLogger(__name__)
LOGO_API = "https://api.coingecko.com/api/v3/search"


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
    if historical.empty:
        raise ValueError(
            f"No historical data returned from cryptocompare API for {token}"
        )
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


class TickerCrypto(TickerBase):
    currency = CRYPTO_CURRENCY

    @classmethod
    def from_config(cls, tt_config, ticker_config) -> "TickerCrypto":
        if tt_config.api_key is None:
            raise ValueError("API key required for crypto ticker.")
        return TickerCrypto(tt_config.api_key, ticker_config)

    def __init__(self, api_key: str, config: TickerConfig) -> None:
        self.api_key = api_key
        cryptocompare.cryptocompare._set_api_key_parameter(self.api_key)
        super().__init__(config)

    def _get_logo(self):
        api = f"{LOGO_API}/?query={self.config.symbol}"
        resp = requests.get(api)
        if not resp.ok:
            return False
        try:
            img = Image.open(
                io.BytesIO(requests.get(resp.json()["coins"][0]["large"]).content)
            )
            if img.mode == "RGBA":
                # remove transparancy make it white
                background = Image.new("RGBA", img.size, (255, 255, 255))
                img = Image.alpha_composite(background, img)
            return img
        except Exception:
            return False

    def _single_tick(self) -> Tuple[pd.DataFrame, Optional[float]]:
        LOGGER.info("Crypto tick: %s", self.config.symbol)
        historical = get_cryptocompare(
            self.config.symbol,
            self.interval_dt,
            self.lookback,
        )
        current = cryptocompare.get_price(self.config.symbol, CRYPTO_CURRENCY)
        current_price: Optional[float] = (
            current[self.config.symbol][CRYPTO_CURRENCY]
            if current is not None
            else None
        )
        return (historical, current_price)
