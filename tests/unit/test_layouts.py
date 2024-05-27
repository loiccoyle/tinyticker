import os
from pathlib import Path
from unittest import TestCase

import pandas as pd
from PIL import Image

from tinyticker import layouts
from tinyticker.config import TickerConfig
from tinyticker.tickers import TickerCrypto
from tinyticker.tickers._base import TickerResponse

UPDATE_REF_PLOTS = os.environ.get("TINYTICKER_UPDATE_REF_PLOTS", False)


class TestLayout(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data_dir = Path(__file__).parents[1] / "data"
        cls.config_path = cls.data_dir / "config.json"
        cls.historical: pd.DataFrame = pd.read_pickle(
            cls.data_dir / "crypto_historical.pkl"
        )
        cls.default = Image.open(cls.data_dir / "layout_default.png").convert("RGB")
        cls.default_volume = Image.open(
            cls.data_dir / "layout_default_volume.png"
        ).convert("RGB")

        cls.dimensions = (250, 122)
        cls.resp = TickerResponse(cls.historical, cls.historical.iloc[-1]["Close"])

    def test_create_fig_ax(self):
        fig, axes = layouts._create_fig_ax(self.dimensions, 2)
        assert len(axes) == 2
        for ax in axes:
            assert ax.margins() == (0, 0)
            assert ax.axison is False
        assert (fig.get_size_inches() * fig.dpi == self.dimensions).all()

    def test_default(self):
        config = TickerConfig(
            symbol="BTC", interval="1h", plot_type="candle", lookback=24, volume=False
        )

        ticker = TickerCrypto("dummy key", config)
        img = layouts.default(self.dimensions, ticker, self.resp)
        assert img.size == self.dimensions
        if UPDATE_REF_PLOTS:
            img.save(self.data_dir / "layout_default.png")
        assert img.tobytes() == self.default.tobytes() or UPDATE_REF_PLOTS

        config.volume = True
        ticker = TickerCrypto("dummy key", config)
        img = layouts.default(self.dimensions, ticker, self.resp)
        assert img.size == self.dimensions
        if UPDATE_REF_PLOTS:
            img.save(self.data_dir / "layout_default_volume.png")
        assert img.tobytes() == self.default_volume.tobytes() or UPDATE_REF_PLOTS
