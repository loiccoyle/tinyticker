import os
from itertools import product
from pathlib import Path
from unittest import TestCase

import pandas as pd

from tinyticker import layouts
from tinyticker.config import TickerConfig
from tinyticker.layouts import LayoutFunc
from tinyticker.tickers import TickerCrypto
from tinyticker.tickers._base import TickerResponse

UPDATE_REF_PLOTS = os.environ.get("TINYTICKER_UPDATE_REF_PLOTS", False)


def _test_layout(layout_func: LayoutFunc, dimensions, resp, data_dir):
    config = TickerConfig(
        symbol="SPY", interval="1d", lookback=30, plot_type="candle", volume=False
    )
    volume = [True, False]
    y_axis = [True, False]
    x_gaps = [True, False]
    for volume, y_axis, x_gap in product(volume, y_axis, x_gaps):
        config.volume = volume
        config.layout.y_axis = y_axis
        config.layout.x_gaps = x_gap

        ticker = TickerCrypto("dummy key", config)
        out = layout_func(dimensions, ticker, resp)
        assert out.size == dimensions
        filename = f"{layout_func.__name__}_{y_axis}_{x_gap}_{volume}.jpg"
        if UPDATE_REF_PLOTS:
            out.save(data_dir / filename)
        assert out.tobytes() == (data_dir / filename).read_bytes() or UPDATE_REF_PLOTS


class TestLayout(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data_dir = Path(__file__).parents[1] / "data"
        cls.layout_dir = cls.data_dir / "layouts"
        cls.config_path = cls.data_dir / "config.json"
        cls.historical: pd.DataFrame = pd.read_pickle(
            cls.data_dir / "stock_historical.pkl"
        )

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
        _test_layout(layouts.default, self.dimensions, self.resp, self.layout_dir)

    def test_big_price(self):
        _test_layout(layouts.big_price, self.dimensions, self.resp, self.layout_dir)
