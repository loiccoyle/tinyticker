import io
from typing import Optional, Tuple

import matplotlib.pyplot as plt
import mplfinance as mpf
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.ticker import FormatStrFormatter
from PIL import Image

from ..config import LayoutConfig
from ..tickers._base import TickerBase, TickerResponse
from ..tickers.stock import TickerStock

CURRENCY_SYMBOLS = {
    "USD": "$",
    "EUR": "€",
    "GBP": "£",
    "JPY": "¥",
    "CNY": "¥",
}
MARKETCOLORS = mpf.make_marketcolors(
    up="white",
    down="black",
    edge="black",
    wick="black",
    ohlc="black",
    volume="black",
)
MARKETCOLORS["vcedge"] = {"up": "black", "down": "black"}
STYLE = mpf.make_mpf_style(marketcolors=MARKETCOLORS, mavcolors=[(1, 0, 0)])
TEXT_BBOX = {
    "boxstyle": "square,pad=0",
    "facecolor": "white",
    "edgecolor": "white",
}


def resize_aspect(image: Image.Image, size: Tuple[int, int]):
    (width, height) = image.size
    (target_width, target_height) = size
    if width < height:
        out = image.resize((round(width * target_height / height), target_height))
    else:
        out = image.resize((target_width, round(height * target_width / width)))
    return out


def fontsize_for_size(
    text_size: Tuple[float, float], fontsize: float, size: Tuple[int, int]
) -> float:
    """Interpolates to get the maximum font size to fit the text within the provided size.

    Args:
        text_size: The text width and height at current font size.
        fontsize: The current font size
        size: The target size to fit the text within.

    Returns:
        The computed font size.
    """
    (text_width, text_height) = text_size
    (width, height) = size
    return min(fontsize * width / text_width, fontsize * height / text_height)


def strip_ax(ax: Axes) -> None:
    """Strip all visuals from `plt.Axes` object."""
    ax.axis(False)
    ax.margins(0, 0)
    ax.grid(False)


def create_fig_ax(
    size: Tuple[int, int], n_axes: int = 1, **kwargs
) -> Tuple[Figure, np.ndarray]:
    """Create the `plt.Figure` and `plt.Axes` used to plot the chart.

    Args:
        size: the size of the plot, (width, height).
        n_axes: the number of subplot axes to create.
        **kwargs: passed to `plt.subplots`.

    Returns:
        The `plt.Figure` and an array of `plt.Axes`.
    """
    width, height = size
    dpi = plt.rcParams.get("figure.dpi", 96)
    px = 1 / dpi
    fig, axes = plt.subplots(
        n_axes,
        1,
        figsize=(width * px, height * px),
        sharex=True,
        frameon=False,
        **kwargs,
    )
    if not isinstance(axes, np.ndarray):
        axes = np.array([axes])
    fig.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
    for ax in axes:
        strip_ax(ax)
    return fig, axes  # type: ignore


def fig_to_image(fig: Figure, tight_layout: bool = True) -> Image.Image:
    """Convert a `plt.Figure` to `PIL.Image.Image`.

    Args:
        fig: The `plt.Figure` to convert.

    Returns:
        The `PIL.Image.Image` representation of the provided `plt.Figure`.
    """
    if tight_layout:
        fig.tight_layout(pad=0)
    with io.BytesIO() as buffer:
        fig.savefig(buffer, format="jpeg", pad_inches=0)
        # to stop the fig from showing up in notebooks and such
        plt.close(fig)
        return Image.open(buffer, formats=("jpeg",)).convert("RGB")


def y_axis(ax: Axes, resp: TickerResponse) -> Axes:
    ax.axis(True)
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(True)
    ax.yaxis.label.set_visible(False)
    ax.spines[["left", "top", "bottom"]].set_visible(False)
    ax.yaxis.set_ticks_position("right")
    ax.yaxis.set_major_formatter(FormatStrFormatter("%.2f"))
    ax.yaxis.set_ticks([resp.historical["Low"].min(), resp.historical["High"].max()])
    ax.yaxis.set_ticklabels(
        ax.yaxis.get_ticklabels(),
        color="black",
        fontsize=8,
        weight="bold",
    )
    ax.yaxis.set_tick_params(pad=0)
    return ax


def x_gaps(ax: Axes, resp: TickerResponse) -> Axes:
    gaps = resp.historical.index.to_series().diff()
    large_gaps = np.arange(0, len(gaps))[gaps > gaps.median()]
    for gap in large_gaps:
        ax.axvline(
            gap - 0.5,
            color="black",
            linestyle=":",
            linewidth=1,
        )
    return ax


def apply_layout_config(
    ax: Axes, layout_config: LayoutConfig, resp: TickerResponse
) -> Axes:
    """Apply the layout configuration to the plot.

    For now we assume only one Axes needs to be modified.

    Args:
        ax: the `plt.Axes` to modify.
        layout_config: the layout configuration to apply.
        resp: the response from the ticker.
    """
    if layout_config.y_axis:
        ax = y_axis(ax, resp)
    if layout_config.x_gaps:
        ax = x_gaps(ax, resp)
    return ax


def historical_plot(
    size: Tuple[int, int], ticker: TickerBase, resp: TickerResponse
) -> Tuple[Figure, Tuple[Axes, Optional[Axes]]]:
    if ticker.config.volume:
        fig, (ax, volume_ax) = create_fig_ax(size, n_axes=2, height_ratios=[3, 1])
    else:
        fig, (ax,) = create_fig_ax(size, n_axes=1)
        volume_ax = False

    kwargs = {}
    if ticker.config.mav:
        kwargs["mav"] = ticker.config.mav

    # if incomplete data, leave space for the missing data
    if len(resp.historical) < ticker.lookback:
        # the floats are to leave padding left and right of the edge candles
        kwargs["xlim"] = (-0.75, ticker.lookback - 0.25)

    ax: Axes
    mpf.plot(
        resp.historical,
        type=ticker.config.plot_type,
        ax=ax,
        volume=volume_ax,
        update_width_config={"line_width": 1},
        style=STYLE,
        linecolor="k",
        **kwargs,
    )
    return fig, (ax, volume_ax if volume_ax else None)


def perc_change(ticker: TickerBase, resp: TickerResponse) -> float:
    if isinstance(ticker, TickerStock):
        perc_change_start = ticker._yf_ticker.fast_info["previous_close"]
    else:
        perc_change_start = resp.historical.iloc[0]["Open"]
    return 100 * (resp.current_price - perc_change_start) / perc_change_start


def perc_change_abp(ticker: TickerBase, resp: TickerResponse) -> float:
    if ticker.config.avg_buy_price is None:
        raise ValueError("No average buy price set.")
    return (
        100
        * (resp.current_price - ticker.config.avg_buy_price)
        / ticker.config.avg_buy_price
    )
