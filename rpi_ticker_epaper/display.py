import logging
from typing import Tuple, Optional

import matplotlib
import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd
from PIL import Image

from .waveshare_lib import CONFIG, EPD


class Display:
    """Handle the displaying of the API response.

    Args:
        coin: Crypto coin, "BTC", "ETH", "DOGE" ...
        currency: Currency code, "USD", "EUR" ...
    """

    def __init__(
        self,
        coin: str,
        currency: str,
        flip: bool = False,
    ) -> None:
        self._log = logging.getLogger(__name__)
        self.coin = coin
        self.currency = currency
        self.previous_response = {}
        self.flip = flip
        self.epd = EPD()
        self.init_epd()

    def init_epd(self):
        """Initialize the ePaper display module."""
        self._log.debug("Init ePaper display.")
        self.epd.init(self.epd.FULL_UPDATE)
        self.epd.Clear(0xFF)

    @staticmethod
    def fig_to_image(fig: plt.Figure) -> Image.Image:
        """Convert a plt.Figure to PIL.Image"""
        matplotlib.use("Agg")
        fig.canvas.draw()
        return Image.frombytes(
            "RGB",
            fig.canvas.get_width_height(),
            fig.canvas.tostring_rgb(),
        )

    def _plot(self) -> Tuple[plt.Figure, plt.Axes]:
        dpi = plt.rcParams.get("figure.dpi", 96)
        px = 1 / dpi
        self._log.debug("Plot width: %s", self.epd.width)
        self._log.debug("Plot height: %s", self.epd.height)
        fig, ax = plt.subplots(figsize=(self.epd.height * px, self.epd.width * px))
        fig.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
        fig.set_dpi(dpi)
        ax.axis("off")
        ax.margins(0, 0)
        return fig, ax

    def text(self, text: str, show: bool = False) -> Tuple[plt.Figure, plt.Axes]:
        """Display text on the display."""
        fig, ax = self._plot()
        ax.text(0, 0, text, ha="center", va="center", wrap=True)
        if show:
            self.show(fig)
        return fig, ax

    def show(self, fig: plt.Figure) -> None:
        """Show a plt.Figure on the display."""
        image = self.fig_to_image(fig)
        image = image.convert("1")
        if self.flip:
            image = image.rotate(180)
        self._log.debug("Image size: %s", image.size)
        self._log.debug("Init display partial.")
        # I think this wakes it from sleep
        self.epd.init(self.epd.FULL_UPDATE)
        # This sets the display mode to partial so the display doesn't flash
        self.epd.init(self.epd.PART_UPDATE)
        self.epd.displayPartial(self.epd.getbuffer(image))
        self._log.debug("Display Sleep")
        self.epd.sleep()

    def plot(
        self,
        historical: dict,
        current_price: Optional[dict],
        sub_string: Optional[str] = None,
        show: bool = False,
    ) -> Tuple[plt.Figure, plt.Axes]:
        df = pd.DataFrame(historical)
        df.set_index("time", inplace=True)
        df.index = pd.to_datetime(df.index, unit="s")  # type: ignore
        df.rename(
            columns={"high": "High", "close": "Close", "low": "Low", "open": "Open"},
            inplace=True,
        )
        fig, ax = self._plot()
        mpf.plot(df, type="candle", ax=ax)
        display_str = f"{self.coin}:{self.currency}"
        if current_price is not None:
            display_str = display_str + f" {current_price[self.coin][self.currency]}"
        text = ax.text(
            0,
            1,
            display_str,
            transform=ax.transAxes,
            fontsize=10,
        )
        text.set_bbox(dict(facecolor="white", edgecolor="white"))
        if sub_string is not None:
            text = ax.text(
                0,
                0.88,
                sub_string,
                transform=ax.transAxes,
                fontsize=8,
            )
            text.set_bbox(dict(facecolor="white", edgecolor="white"))

        fig.tight_layout(pad=0)
        if show:
            self.show(fig)
        return fig, ax

    def __del__(self):
        CONFIG.module_exit()
