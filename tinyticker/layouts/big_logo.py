from typing import Tuple, Union

from PIL import Image, ImageDraw, ImageFont

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
    resize_aspect,
)


def ttf_font_or_default(
    font: str, size: int = 10
) -> Union[ImageFont.FreeTypeFont, ImageFont.ImageFont]:
    try:
        return ImageFont.truetype(font, size)
    except OSError:
        return ImageFont.load_default(size)


@register
def big_logo(
    size: Tuple[int, int], ticker: TickerBase, resp: TickerResponse
) -> Image.Image:
    # some layout settings
    padding = min(8, int(0.05 * size[0]))
    half_padding = round(padding / 2)
    logo_height = int(size[0] * 0.4) - 2 * padding
    logo_width = logo_height

    plot_width = size[0] - (logo_width + 2 * padding)

    # DejaVuSans seems to be installed by default on RPis
    monospace_font_file = "DejaVuSansMono-Bold.ttf"
    regular_font_file = "DejaVuSans-Bold.ttf"
    default_size = 10
    monospace_font = ttf_font_or_default(monospace_font_file, default_size)
    regular_font = ttf_font_or_default(regular_font_file, default_size)

    range_text = f"{len(resp.historical)}x{ticker.config.interval} {perc_change(ticker, resp):+.2f}%"
    if ticker.config.avg_buy_price:
        range_text += f" ({perc_change_abp(ticker, resp):+.2f}%)"
    range_text_bbox = monospace_font.getbbox(range_text)
    range_text_font = ttf_font_or_default(
        monospace_font_file,
        size=round(
            fontsize_for_size(
                (range_text_bbox[2], range_text_bbox[3]),
                default_size,
                (plot_width, 14),
            ),
        ),
    )
    plot_size = (plot_width, logo_height - range_text_font.getbbox(range_text)[3])

    fig, axes = historical_plot(plot_size, ticker, resp)
    apply_layout_config(axes[0], ticker.config.layout, resp)
    axes[0].axhline(
        resp.historical[["Open", "High", "Low", "Close"]].mean().mean(),
        linestyle="dotted",
        linewidth=1,
        color="k",
    )
    img_plot = fig_to_image(fig)

    img = Image.new("RGB", size, "#ffffff")
    img.paste(img_plot, (logo_width + 2 * padding, half_padding))
    draw = ImageDraw.Draw(img)

    draw.text(
        (logo_width + 2 * padding, plot_size[1] + half_padding),
        range_text,
        font=range_text_font,
        fill=0,
    )
    available_space = size[1] - (plot_size[1] + (range_text_bbox[3]))

    price_text = f"{CURRENCY_SYMBOLS.get(ticker.currency, '$')}{resp.current_price:.2f}"
    price_text_bbox = regular_font.getbbox(price_text)

    fontsize = fontsize_for_size(
        (price_text_bbox[2], price_text_bbox[3]),
        default_size,
        (size[0] - 2 * padding, available_space - padding),
    )
    price_font = ttf_font_or_default(regular_font_file, size=round(fontsize))
    draw.text(
        (size[0] / 2, size[1]),
        price_text,
        fill=0,
        font=price_font,
        anchor="md",
    )

    if ticker.config.layout.show_logo and ticker.logo:
        img.paste(
            resize_aspect(ticker.logo, (logo_width, logo_height)), (padding, padding)
        )
    else:
        # if we don't have a logo, show the ticker symbol
        symbol_text_bbox = regular_font.getbbox(ticker.config.symbol)
        fontsize = fontsize_for_size(
            (symbol_text_bbox[2], symbol_text_bbox[3]),
            default_size,
            (logo_width, logo_height),
        )
        draw.text(
            (padding + logo_width / 2, padding + logo_height / 2),
            ticker.config.symbol,
            anchor="mm",
            font=ttf_font_or_default(
                regular_font_file,
                size=round(
                    fontsize_for_size(
                        (symbol_text_bbox[2], symbol_text_bbox[3]),
                        default_size,
                        (logo_width, logo_height),
                    )
                ),
            ),
            fill=0,
        )

    return img
