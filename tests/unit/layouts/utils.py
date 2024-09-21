import os
from itertools import product

from PIL import Image

from tinyticker.config import TickerConfig
from tinyticker.layouts.register import LayoutFunc
from tinyticker.tickers import TickerStock

from ..utils import DATA_DIR

LAYOUT_DIR = DATA_DIR / "layouts"
UPDATE_REF_PLOTS = os.environ.get("TINYTICKER_UPDATE_REF_PLOTS", False)
DIMENSIONS = (250, 122)


def layout_test(layout_func: LayoutFunc, dimensions, resp, data_dir):
    config = TickerConfig(
        symbol="AAPL", interval="1d", lookback=30, plot_type="candle", volume=False
    )
    volume = [True, False]
    y_axis = [True, False]
    x_gaps = [True, False]
    for volume, y_axis, x_gap in product(volume, y_axis, x_gaps):
        config.volume = volume
        config.layout.y_axis = y_axis
        config.layout.x_gaps = x_gap

        ticker = TickerStock(config)
        out = layout_func(dimensions, ticker, resp)
        assert out.size == dimensions
        filename = f"{layout_func.__name__}_{y_axis}_{x_gap}_{volume}.png"
        if UPDATE_REF_PLOTS:
            out.save(data_dir / filename)
        assert (
            out.tobytes() == Image.open(data_dir / filename).tobytes()
            or UPDATE_REF_PLOTS
        )
