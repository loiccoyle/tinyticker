"""Layouts are responsible for generating an image for a given dimension, ticker, and response.

They should not care about the capabilities of the display device, only about the content to display.
"""

import dataclasses as dc
import logging
from typing import Callable, Optional, Tuple

import matplotlib.pyplot as plt
import mplfinance as mpf
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from PIL import Image

from .tickers._base import TickerBase, TickerResponse

MARKETCOLORS = mpf.make_marketcolors(
    up="white",
    down="black",
    edge="black",
    wick="black",
    ohlc="black",
    volume="black",
)
MARKETCOLORS["vcedge"] = {"up": "black", "down": "black"}
STYLE = mpf.make_mpf_style(marketcolors=MARKETCOLORS, mavcolors=["r"])
TEXT_BBOX = {
    "boxstyle": "square,pad=0",
    "facecolor": "white",
    "edgecolor": "white",
}
LAYOUTS = {}

Dimensions = Tuple[int, int]
LayoutFunc = Callable[[Dimensions, TickerBase, TickerResponse], Image.Image]

logger = logging.getLogger(__name__)


def _strip_ax(ax: Axes) -> None:
    """Strip all visuals from `plt.Axes` object."""
    ax.axis(False)
    ax.margins(0, 0)
    ax.grid(False)


def _create_fig_ax(
    dimensions: Dimensions, n_axes: int = 1, **kwargs
) -> Tuple[Figure, np.ndarray]:
    """Create the `plt.Figure` and `plt.Axes` used to plot the chart.

    Args:
        dimensions: the dimensions of the plot, (width, height).
        n_axes: the number of subplot axes to create.
        **kwargs: passed to `plt.subplots`.

    Returns:
        The `plt.Figure` and an array of `plt.Axes`.
    """
    width, height = dimensions
    dpi = plt.rcParams.get("figure.dpi", 96)
    px = 1 / dpi
    fig, axes = plt.subplots(
        n_axes,
        1,
        figsize=(width * px, height * px),
        sharex=True,
        **kwargs,
    )
    if not isinstance(axes, np.ndarray):
        axes = np.array([axes])
    fig.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
    for ax in axes:
        _strip_ax(ax)
    return fig, axes  # type: ignore


def _fig_to_image(fig: Figure) -> Image.Image:
    """Convert a `plt.Figure` to `PIL.Image.Image`.

    Args:
        fig: The `plt.Figure` to convert.

    Returns:
        The `PIL.Image.Image` representation of the provided `plt.Figure`.
    """
    fig.canvas.draw()
    return Image.fromarray(
        np.asarray(fig.canvas.buffer_rgba()),  # type: ignore
        mode="RGBA",
    ).convert("RGB")


def register(func: LayoutFunc) -> LayoutFunc:
    """Register a layout function.
    Args:
        func: the layout function to register.
    Returns:
        The layout function.
    """
    layout = Layout(func=func, name=func.__name__, desc=func.__doc__)
    LAYOUTS[layout.name] = layout
    return func


@dc.dataclass
class Layout:
    func: LayoutFunc
    name: str
    desc: Optional[str]


@register
def default(
    dimensions: Dimensions, ticker: TickerBase, resp: TickerResponse
) -> Image.Image:
    """Default layout."""

    delta_range_start = resp.historical.iloc[0]["Open"]
    delta_range = 100 * (resp.current_price - delta_range_start) / delta_range_start

    top_string = f"{ticker.config.symbol}: $ {resp.current_price:.2f}"
    if ticker.config.avg_buy_price is not None:
        # calculate the delta from the average buy price
        delta_abp = (
            100
            * (resp.current_price - ticker.config.avg_buy_price)
            / ticker.config.avg_buy_price
        )
        top_string += f" {delta_abp:+.2f}%"
    sub_string = f"{len(resp.historical)}x{ticker.config.interval} {delta_range:+.2f}%"

    kwargs = {}
    if ticker.config.mav:
        kwargs["mav"] = ticker.config.mav

    # if incomplete data, leave space for the missing data
    if len(resp.historical) < ticker.lookback:
        # the floats are to leave padding left and right of the edge candles
        kwargs["xlim"] = (-0.75, ticker.lookback - 0.25)

    if ticker.config.volume:
        fig, (ax, volume_ax) = _create_fig_ax(
            dimensions, n_axes=2, gridspec_kw={"height_ratios": [3, 1]}
        )
    else:
        fig, (ax,) = _create_fig_ax(dimensions, n_axes=1)
        volume_ax = False
    ax: Axes
    volume_ax: Axes | bool
    mpf.plot(
        resp.historical,
        type=ticker.config.plot_type,
        ax=ax,
        update_width_config={"line_width": 1},
        style=STYLE,
        volume=volume_ax,
        linecolor="k",
        **kwargs,
    )

    top_text = ax.text(
        0,
        1,
        top_string,
        transform=ax.transAxes,
        fontsize=10,
        weight="bold",
        bbox=TEXT_BBOX,
        verticalalignment="top",
    )
    ax_height = ax.get_position().height * dimensions[1]
    ax.text(
        0,
        (ax_height - top_text.get_window_extent().height + 1) / ax_height,
        sub_string,
        transform=ax.transAxes,
        fontsize=8,
        weight="bold",
        bbox=TEXT_BBOX,
        verticalalignment="top",
    )
    gaps = resp.historical.index.to_series().diff()
    large_gaps = np.arange(0, len(gaps))[gaps > gaps.median()]
    for gap in large_gaps:
        ax.axvline(
            gap - 0.5,
            color="black",
            linestyle=":",
            linewidth=1,
        )

    return _fig_to_image(fig)
