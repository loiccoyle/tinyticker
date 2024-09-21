from unittest import IsolatedAsyncioTestCase

from tinyticker import config
from tinyticker.sequence import Sequence
from tinyticker.tickers.crypto import TickerCrypto
from tinyticker.tickers.stock import TickerStock

from .utils import CONFIG_PATH, API_KEY


def test_sequence_from_tt_config():
    tt_config = config.TinytickerConfig.from_file(CONFIG_PATH)
    sequence = Sequence.from_tinyticker_config(tt_config)
    assert len(sequence.tickers) == len(tt_config.tickers)
    assert sequence.skip_empty is True
    assert sequence.skip_outdated is True
    assert isinstance(sequence.tickers[0], TickerStock)
    assert isinstance(sequence.tickers[1], TickerCrypto)


class TestSequenceStart(IsolatedAsyncioTestCase):
    async def test_sequence_order(self):
        if API_KEY is None:
            raise ValueError("CRYPTOCOMPARE_API_KEY not set")

        sequence = Sequence(
            [
                TickerStock(
                    config.TickerConfig(
                        symbol="SPY",
                        symbol_type="stock",
                        interval="1d",
                        lookback=30,
                    )
                ),
                TickerCrypto(
                    API_KEY,
                    config.TickerConfig(
                        symbol_type="crypto",
                        symbol="BTC",
                        interval="1h",
                        lookback=24,
                    ),
                ),
            ],
            skip_outdated=False,  # all data is outdated due to monkey patching
        )
        # no wait time to speed up testing
        for ticker_ in sequence.tickers:
            ticker_.config.wait_time = 0
        i = 0
        async for ticker_, _ in sequence.start():
            assert ticker_.config.symbol == sequence.tickers[i % 2].config.symbol
            i += 1
            if i == 5:
                break
