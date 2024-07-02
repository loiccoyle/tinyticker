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
    strip_ax,
)


@register
def default(
    size: Tuple[int, int], ticker: TickerBase, resp: TickerResponse
) -> Image.Image:
    """Default layout."""
    show_logo = ticker.config.layout.show_logo and ticker.logo
    top_string = f"{CURRENCY_SYMBOLS.get(ticker.currency, '$')}{resp.current_price:.2f}"
    if not show_logo:
        top_string = f"{ticker.config.symbol} {top_string}"
    if ticker.config.avg_buy_price is not None:
        # calculate the delta from the average buy price
        top_string += f" {perc_change_abp(ticker, resp):+.2f}%"

    fig, (ax, _) = historical_plot(size, ticker, resp)
    ax = apply_layout_config(ax, ticker.config.layout, resp)
    fig.tight_layout(pad=0)

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
    pos = ax.get_position()

    sub_text = ax.text(
        0,
        1 - (top_text.get_window_extent().height + 1) / (pos.height * size[1]),
        f"{len(resp.historical)}x{ticker.config.interval} {perc_change(ticker, resp):+.2f}%",
        transform=ax.transAxes,
        fontsize=8,
        weight="bold",
        bbox=TEXT_BBOX,
        verticalalignment="top",
    )

    if show_logo:
        # add the logo and shift the text to the right
        logo_height_abs = (
            top_text.get_window_extent().height
            + sub_text.get_window_extent().height
            + 2
        )
        logo_height = logo_height_abs / size[1]
        logo_width = logo_height_abs / size[0]
        top_text.set_position(
            (
                top_text.get_position()[0] + logo_width * 1 / pos.width,
                top_text.get_position()[1],
            )
        )
        sub_text.set_position((logo_width * 1 / pos.width, sub_text.get_position()[1]))

        img_ax = fig.add_axes(
            (
                ax.get_position().x0,
                ax.get_position().y1 - logo_height,
                logo_width,
                logo_height,
            )
        )
        img_ax.imshow(ticker.logo, aspect="equal")
        strip_ax(img_ax)

    return fig_to_image(fig, tight_layout=False)
