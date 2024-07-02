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
    strip_ax,
)


@register
def big_price(
    size: Tuple[int, int], ticker: TickerBase, resp: TickerResponse
) -> Image.Image:
    """Big price layout."""
    show_logo = ticker.config.layout.show_logo and ticker.logo
    fig, (ax, _) = historical_plot(size, ticker, resp)

    top_string = f"{CURRENCY_SYMBOLS.get(ticker.currency, '$')}{resp.current_price:.2f}"
    if not show_logo:
        top_string = f"{ticker.config.symbol} {top_string}"

    suptitle_text = fig.suptitle(
        top_string,
        weight="bold",
        x=0,
        y=1,
        horizontalalignment="left",
        fontsize=18,
    )
    suptitle_text.set_fontsize(
        fontsize_for_size(
            (
                suptitle_text.get_window_extent().width,
                suptitle_text.get_window_extent().height,
            ),
            18,
            (size[0], 22),
        )
    )

    sub_string = f"{len(resp.historical)}x{ticker.config.interval} {perc_change(ticker, resp):+.2f}%"
    if ticker.config.avg_buy_price:
        sub_string += f" ({perc_change_abp(ticker, resp):+.2f}%)"

    title_text = ax.set_title(
        sub_string,
        weight="bold",
        loc="left",
        fontsize=12,
    )
    title_text.set_fontsize(
        fontsize_for_size(
            (
                title_text.get_window_extent().width,
                title_text.get_window_extent().height,
            ),
            12,
            (
                round(
                    size[0]
                    - (
                        suptitle_text.get_window_extent().height * 2
                        if ticker.logo
                        else 0
                    )
                ),
                18,
            ),
        )
    )
    ax = apply_layout_config(ax, ticker.config.layout, resp)
    fig.tight_layout(pad=0)

    if show_logo:
        # add the logo and shift the text to the right
        logo_height_abs = (
            suptitle_text.get_window_extent().height
            + title_text.get_window_extent().height
            + 2
        )
        logo_height = logo_height_abs / size[1]
        logo_width = logo_height_abs / size[0]
        suptitle_text.set_position(
            (
                suptitle_text.get_position()[0] + logo_width,
                suptitle_text.get_position()[1],
            )
        )
        title_text.set_position(
            (
                title_text.get_position()[0] + logo_width * 1 / ax.get_position().width,
                title_text.get_position()[1],
            )
        )

        img_ax = fig.add_axes(
            (
                0,
                1 - logo_height,
                logo_width,
                logo_height,
            )
        )
        img_ax.imshow(ticker.logo, aspect="equal")
        strip_ax(img_ax)

    # ax = apply_layout_config(ax, ticker.config.layout, resp)
    return fig_to_image(fig, tight_layout=False)
