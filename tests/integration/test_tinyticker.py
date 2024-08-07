"""
These tests are meant to be run on an RPi configured with the Tinyticker disk image and
an EPDbc 2.13 inch display.
"""

import os
import typing
from datetime import timezone
from itertools import product
from unittest import IsolatedAsyncioTestCase

import pandas as pd
import pytest

from tinyticker import (
    Display,
    Sequence,
    TickerConfig,
    TinytickerConfig,
    utils,
)
from tinyticker.config import PLOT_TYPES
from tinyticker.paths import CONFIG_FILE

# monkey patch the now function so tests are time indenpendent
utils.__dict__["now"] = lambda: pd.Timestamp(
    2021, 7, 22, 18, 00, 00, tzinfo=timezone.utc
)


def _get_api_key():
    api_key = os.environ.get("CRYPTOCOMPARE_API_KEY", None)
    if api_key is None:
        api_key = TinytickerConfig.from_file(CONFIG_FILE).api_key
    if api_key is None:
        raise ValueError("No API key found.")
    return api_key


@typing.no_type_check
def _create_tickers():
    wait_times = [1]
    plot_types = PLOT_TYPES
    preposts = [False, True]
    avg_buy_prices = [None, 100]
    symbols = [("SPY", "stock"), ("BTC", "crypto")]
    mavs = [None, 3]
    volumes = [False, True]

    iter = product(
        symbols,
        plot_types,
        wait_times,
        preposts,
        avg_buy_prices,
        mavs,
        volumes,
    )

    tickers = []
    for (
        symbol,
        symbol_type,
    ), plot_type, wait_time, prepost, avg_buy_price, mav, volume in iter:
        # prepost does nothing for crypto tickers
        if prepost and symbol_type == "crypto":
            continue
        tickers.append(
            TickerConfig(
                symbol=symbol,
                symbol_type=symbol_type,
                wait_time=wait_time,
                plot_type=plot_type,
                prepost=prepost,
                avg_buy_price=avg_buy_price,
                mav=mav,
                volume=volume,
            )
        )
    return tickers


class TestTinyticker(IsolatedAsyncioTestCase):
    @pytest.mark.skipif(
        os.uname().nodename != "TinyTicker", reason="Not on Tinyticker rpi"
    )
    async def test_tinyticker(self):
        epd_model = "EPDbc"  # the EPD model I have
        tickers = _create_tickers()

        tt_config = TinytickerConfig(
            api_key=_get_api_key(),
            epd_model=epd_model,
            tickers=tickers,
            flip=True,
        )
        sequence = Sequence.from_tinyticker_config(tt_config)
        display = Display.from_tinyticker_config(tt_config)

        i = 0
        async for ticker, resp in sequence.start():
            print(f"Showing ticker #{i+1}/{len(sequence.tickers)}: {ticker.config}")
            display.show(ticker, resp)
            if i == len(sequence.tickers) - 1:
                break
            i += 1
