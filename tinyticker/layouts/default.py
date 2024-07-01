from typing import Tuple

from PIL import Image

from ..tickers._base import TickerBase, TickerResponse
from .register import register
from .utils import (
    CURRENCY_SYMBOLS,
    TEXT_BBOX,
    apply_layout_config,
    fig_to_image,
    historical_plot,
    perc_change,
    perc_change_abp,
)


@register
def default(
    size: Tuple[int, int], ticker: TickerBase, resp: TickerResponse
) -> Image.Image:
    """Default layout."""

    top_string = f"{ticker.config.symbol} {CURRENCY_SYMBOLS.get(ticker.currency, '$')}{resp.current_price:.2f}"
    if ticker.config.avg_buy_price is not None:
        # calculate the delta from the average buy price
        top_string += f" {perc_change_abp(ticker, resp):+.2f}%"

    fig, (ax, _) = historical_plot(size, ticker, resp)

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
        f"{len(resp.historical)}x{ticker.config.interval} {perc_change(ticker, resp):+.2f}%",
        transform=ax.transAxes,
        fontsize=8,
        weight="bold",
        bbox=TEXT_BBOX,
        verticalalignment="top",
    )

    ax = apply_layout_config(ax, ticker.config.layout, resp)
    return fig_to_image(fig)
