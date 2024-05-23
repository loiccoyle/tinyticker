import os
from pathlib import Path
from unittest import IsolatedAsyncioTestCase, TestCase

from tinyticker import config
from tinyticker.sequence import Sequence
from tinyticker.tickers.crypto import TickerCrypto
from tinyticker.tickers.stock import TickerStock

API_KEY = os.environ.get("CRYPTOCOMPARE_API_KEY", None)


class TestSequence(TestCase):
    @classmethod
    def setUpClass(cls):
        if API_KEY is None:
            raise ValueError("CRYPTOCOMPARE_API_KEY not set")
        cls.data_dir = Path(__file__).parents[1] / "data"
        cls.config_path = cls.data_dir / "config.json"

    def test_sequence_from_tt_config(self):
        tt_config = config.TinytickerConfig.from_file(self.config_path)
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
            ticker_.wait_time = 0
        i = 0
        async for ticker_, _ in sequence.start():
            assert ticker_.config.symbol == sequence.tickers[i % 2].config.symbol
            i += 1
            if i == 5:
                break
