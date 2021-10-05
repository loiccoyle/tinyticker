import logging
from typing import Tuple

import matplotlib
import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd
from PIL import Image

from .waveshare_lib import CONFIG, EPD

CURRENCY_SYMBOLS = {"USD": "$", "EUR": "€", "GBP": "£"}


class Display:
    """Handle the displaying of the API response."""

    def __init__(
        self,
        coin: str,
        currency: str,
    ) -> None:
        self._log = logging.getLogger(__name__)
        self.coin = coin
        self.currency = currency
        self.previous_response = {}
        self.epd = EPD()
        self.init_epd()

    def init_epd(self):
        self._log.debug("Init ePaper display.")
        self.epd.init(self.epd.FULL_UPDATE)
        self.epd.Clear(0xFF)
        self.epd.init(self.epd.PART_UPDATE)

    @staticmethod
    def fig_to_image(fig: plt.Figure) -> Image.Image:
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

    def text(self, text: str) -> None:
        fig, ax = self._plot()
        ax.text(0, 0, text, ha="center", va="center", wrap=True)
        self.show(fig)

    def show(self, fig: plt.Figure) -> None:
        image = self.fig_to_image(fig)
        image = image.convert("1")
        self._log.debug("Image size: %s", image.size)
        self.epd.displayPartial(self.epd.getbuffer(image))

    def response(self, response: dict) -> None:
        fig, _ = self.plot(response)
        self.show(fig)

    def plot(self, response: dict) -> Tuple[plt.Figure, plt.Axes]:
        df = pd.DataFrame(response)
        df.set_index("time", inplace=True)
        df.index = pd.to_datetime(df.index, unit="s")  # type: ignore
        df.rename(
            columns={"high": "High", "close": "Close", "low": "Low", "open": "Open"},
            inplace=True,
        )
        fig, ax = self._plot()
        mpf.plot(df, type="candle", ax=ax)
        ax.text(
            0.5,
            1,
            f"{self.coin}:{self.currency}",
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=10,
        )
        fig.tight_layout(pad=0)
        return fig, ax

    def __del__(self):
        CONFIG.module_exit()
