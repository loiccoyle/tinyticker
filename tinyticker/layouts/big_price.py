from typing import Tuple

from PIL import Image

from ..tickers._base import TickerBase, TickerResponse
from .register import register
from .utils import (
    CURRENCY_SYMBOLS,
    apply_layout_config,
    fig_to_image,
    fontsize_for_size,
    historical_plot,
    perc_change,
    perc_change_abp,
)


@register
def big_price(
    size: Tuple[int, int], ticker: TickerBase, resp: TickerResponse
) -> Image.Image:
    """Big price layout."""
    fig, (ax, _) = historical_plot(size, ticker, resp)
    text = fig.suptitle(
        f"{ticker.config.symbol} {CURRENCY_SYMBOLS.get(ticker.currency, '$')}{resp.current_price:.2f}",
        weight="bold",
        x=0,
        y=1,
        horizontalalignment="left",
        fontsize=18,
    )
    text.set_fontsize(
        fontsize_for_size(
            (text.get_window_extent().width, text.get_window_extent().height),
            18,
            (size[0], 22),
        )
    )

    sub_string = f"{len(resp.historical)}x{ticker.config.interval} {perc_change(ticker, resp):+.2f}%"
    if ticker.config.avg_buy_price:
        sub_string += f" ({perc_change_abp(ticker, resp):+.2f}%)"

    text = ax.set_title(
        sub_string,
        weight="bold",
        loc="left",
        fontsize=12,
    )
    text.set_fontsize(
        fontsize_for_size(
            (text.get_window_extent().width, text.get_window_extent().height),
            12,
            (size[0], 18),
        )
    )

    ax = apply_layout_config(ax, ticker.config.layout, resp)
    return fig_to_image(fig)
