"""Layouts are responsible for generating an image for a given size, ticker, and response.

They should not care about the capabilities of the display device, only about the content to display.
"""

import dataclasses as dc
import io
import logging
from typing import Callable, Optional, Tuple, Union

import matplotlib.pyplot as plt
import mplfinance as mpf
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.ticker import FormatStrFormatter
from PIL import Image, ImageDraw, ImageFont

from .config import LayoutConfig
from .tickers._base import TickerBase, TickerResponse
from .tickers.stock import TickerStock

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
CURRENCY_SYMBOLS = {
    "USD": "$",
    "EUR": "€",
    "GBP": "£",
    "JPY": "¥",
    "CNY": "¥",
}
LAYOUTS = {}

Size = Tuple[int, int]
LayoutFunc = Callable[[Size, TickerBase, TickerResponse], Image.Image]

logger = logging.getLogger(__name__)


def _resize_aspect(image: Image.Image, size: Tuple[int, int]):
    (width, height) = image.size
    (target_width, target_height) = size
    if width < height:
        out = image.resize((round(width * target_height / height), target_height))
    else:
        out = image.resize((target_width, round(height * target_width / width)))
    return out


def _fontsize_for_size(
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


def _strip_ax(ax: Axes) -> None:
    """Strip all visuals from `plt.Axes` object."""
    ax.axis(False)
    ax.margins(0, 0)
    ax.grid(False)


def _create_fig_ax(size: Size, n_axes: int = 1, **kwargs) -> Tuple[Figure, np.ndarray]:
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
        _strip_ax(ax)
    return fig, axes  # type: ignore


def _fig_to_image(fig: Figure) -> Image.Image:
    """Convert a `plt.Figure` to `PIL.Image.Image`.

    Args:
        fig: The `plt.Figure` to convert.

    Returns:
        The `PIL.Image.Image` representation of the provided `plt.Figure`.
    """
    fig.tight_layout(pad=0)
    with io.BytesIO() as buffer:
        fig.savefig(buffer, format="jpeg", pad_inches=0)
        # to stop the fig from showing up in notebooks and such
        plt.close(fig)
        return Image.open(buffer, formats=("jpeg",)).convert("RGB")


def register(func: LayoutFunc) -> LayoutFunc:
    """Register a layout function.

    Args:
        func: the layout function to register.

    Returns:
        The layout function.
    """
    layout = Layout(func=func, name=func.__name__.replace("_", " "), desc=func.__doc__)
    LAYOUTS[layout.name] = layout
    return func


@dc.dataclass
class Layout:
    func: LayoutFunc
    name: str
    desc: Optional[str]


def _y_axis(ax: Axes, resp: TickerResponse) -> Axes:
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


def _x_gaps(ax: Axes, resp: TickerResponse) -> Axes:
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
        ax = _y_axis(ax, resp)
    if layout_config.x_gaps:
        ax = _x_gaps(ax, resp)
    return ax


def _historical_plot(
    size: Size, ticker: TickerBase, resp: TickerResponse
) -> Tuple[Figure, Tuple[Axes, Optional[Axes]]]:
    if ticker.config.volume:
        fig, (ax, volume_ax) = _create_fig_ax(size, n_axes=2, height_ratios=[3, 1])
    else:
        fig, (ax,) = _create_fig_ax(size, n_axes=1)
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


def _perc_change(ticker: TickerBase, resp: TickerResponse) -> float:
    if isinstance(ticker, TickerStock):
        perc_change_start = ticker._yf_ticker.fast_info["previous_close"]
    else:
        perc_change_start = resp.historical.iloc[0]["Open"]
    return 100 * (resp.current_price - perc_change_start) / perc_change_start


def _perc_change_abp(ticker: TickerBase, resp: TickerResponse) -> float:
    if ticker.config.avg_buy_price is None:
        raise ValueError("No average buy price set.")
    return (
        100
        * (resp.current_price - ticker.config.avg_buy_price)
        / ticker.config.avg_buy_price
    )


@register
def default(size: Size, ticker: TickerBase, resp: TickerResponse) -> Image.Image:
    """Default layout."""

    perc_change = _perc_change(ticker, resp)

    top_string = f"{ticker.config.symbol} {CURRENCY_SYMBOLS.get(ticker.currency, '$')}{resp.current_price:.2f}"
    if ticker.config.avg_buy_price is not None:
        # calculate the delta from the average buy price
        top_string += f" {_perc_change_abp(ticker, resp):+.2f}%"

    fig, (ax, _) = _historical_plot(size, ticker, resp)

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
    ax_height = ax.get_position().height * size[1]
    ax.text(
        0,
        (ax_height - top_text.get_window_extent().height + 1) / ax_height,
        f"{len(resp.historical)}x{ticker.config.interval} {perc_change:+.2f}%",
        transform=ax.transAxes,
        fontsize=8,
        weight="bold",
        bbox=TEXT_BBOX,
        verticalalignment="top",
    )

    ax = apply_layout_config(ax, ticker.config.layout, resp)
    return _fig_to_image(fig)


@register
def big_price(size: Size, ticker: TickerBase, resp: TickerResponse) -> Image.Image:
    """Big price layout."""
    perc_change = _perc_change(ticker, resp)
    fig, (ax, _) = _historical_plot(size, ticker, resp)
    text = fig.suptitle(
        f"{ticker.config.symbol} {CURRENCY_SYMBOLS.get(ticker.currency, '$')}{resp.current_price:.2f}",
        weight="bold",
        x=0,
        y=1,
        horizontalalignment="left",
        fontsize=18,
    )
    text.set_fontsize(
        _fontsize_for_size(
            (text.get_window_extent().width, text.get_window_extent().height),
            18,
            (size[0], 22),
        )
    )

    sub_string = f"{len(resp.historical)}x{ticker.config.interval} {perc_change:+.2f}%"
    if ticker.config.avg_buy_price:
        sub_string += f" ({_perc_change_abp(ticker, resp):+.2f}%)"

    text = ax.set_title(
        sub_string,
        weight="bold",
        loc="left",
        fontsize=12,
    )
    text.set_fontsize(
        _fontsize_for_size(
            (text.get_window_extent().width, text.get_window_extent().height),
            12,
            (size[0], 18),
        )
    )

    ax = apply_layout_config(ax, ticker.config.layout, resp)
    return _fig_to_image(fig)


@register
def logo(size: Size, ticker: TickerBase, resp: TickerResponse) -> Image.Image:
    # some layout settings
    padding = min(8, int(0.05 * size[0]))
    half_padding = round(padding / 2)
    logo_height = int(size[0] * 0.4) - 2 * padding
    logo_width = logo_height

    def ttf_font_or_default(
        font: str, size: int = 10
    ) -> Union[ImageFont.FreeTypeFont, ImageFont.ImageFont]:
        try:
            return ImageFont.truetype(font, size)
        except OSError:
            return ImageFont.load_default(size)

    # DejaVuSans seems to be installed by default on RPis
    monospace_font = ttf_font_or_default("DejaVuSansMono.ttf", 12)
    regular_font = ttf_font_or_default("DejaVuSans-Bold.ttf")

    range_text = f"{len(resp.historical)}x{ticker.config.interval} {_perc_change(ticker, resp):+.2f}%"
    range_text_bbox = monospace_font.getbbox(range_text)
    plot_size = (size[0] - (logo_width + 2 * padding), logo_height - range_text_bbox[3])

    fig, axes = _historical_plot(plot_size, ticker, resp)
    apply_layout_config(axes[0], ticker.config.layout, resp)
    axes[0].axhline(
        resp.historical[["Open", "High", "Low", "Close"]].mean().mean(),
        linestyle="dotted",
        linewidth=1,
        color="k",
    )
    img_plot = _fig_to_image(fig)

    img = Image.new("RGB", size, "#ffffff")
    img.paste(img_plot, (size[0] - plot_size[0] - half_padding, half_padding))
    draw = ImageDraw.Draw(img)

    if ticker.config.avg_buy_price:
        range_text += f" ({_perc_change_abp(ticker, resp):+.2f}%)"

    draw.text(
        (size[0] - plot_size[0] - half_padding, plot_size[1] + half_padding),
        range_text,
        font=monospace_font,
        fill=0,
    )
    available_space = size[1] - (plot_size[1] + (range_text_bbox[3]))

    regular_font = ImageFont.truetype("DejaVuSans.ttf")
    price_text = f"{CURRENCY_SYMBOLS.get(ticker.currency, '$')}{resp.current_price:.2f}"
    price_text_bbox = regular_font.getbbox(price_text)

    fontsize = _fontsize_for_size(
        (price_text_bbox[2], price_text_bbox[3]),
        regular_font.size,
        (size[0] - 2 * padding, available_space - padding),
    )
    price_font = ImageFont.truetype(regular_font.path, size=round(fontsize))
    draw.text(
        (size[0] / 2, size[1]),
        price_text,
        fill=0,
        font=price_font,
        anchor="md",
    )

    if ticker.logo:
        img.paste(
            _resize_aspect(ticker.logo, (logo_width, logo_height)), (padding, padding)
        )
    else:
        # if we don't have a logo, show the ticker symbol
        symbol_text_bbox = regular_font.getbbox(ticker.config.symbol)
        fontsize = _fontsize_for_size(
            (symbol_text_bbox[2], symbol_text_bbox[3]),
            regular_font.size,
            (logo_width, logo_height),
        )
        symbol_font = ImageFont.truetype(regular_font.path, size=round(fontsize))

        pos = (padding + logo_width / 2, padding + logo_height / 2)
        draw.rounded_rectangle(
            draw.textbbox(
                pos,
                ticker.config.symbol,
                anchor="mm",
                # a bit bigger to have some margin
                font=ImageFont.truetype(
                    symbol_font.path, size=round(symbol_font.size * 1.2)
                ),
            ),
            4,
            fill="#cccccc",
        )
        draw.text(pos, ticker.config.symbol, anchor="mm", font=symbol_font, fill=0)

    return img
