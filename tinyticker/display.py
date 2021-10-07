import logging
from typing import List, Optional, Tuple

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
        flip: Flip the display.
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
        self._log.info("Init ePaper display.")
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
            self.show_fig(fig)
        return fig, ax

    def show_fig(self, fig: plt.Figure) -> None:
        """Show a `plt.Figure` on the display."""
        image = self.fig_to_image(fig)
        image = image.convert("1")
        self.show_image(image)

    def show_image(self, image: Image.Image) -> None:
        """Show a `PIL.Image.Image` on the display."""
        if self.flip:
            image = image.rotate(180)
        self._log.debug("Image size: %s", image.size)
        self._log.info("Init display partial.")
        # I think this wakes it from sleep
        self.epd.init(self.epd.FULL_UPDATE)
        self.epd.display(self.epd.getbuffer(image))
        self._log.info("Display sleep.")
        self.epd.sleep()

    def plot(
        self,
        historical: List[dict],
        current_price: Optional[dict],
        sub_string: Optional[str] = None,
        show: bool = False,
        type: str = "candle",
        **kwargs,
    ) -> Tuple[plt.Figure, plt.Axes]:
        """Plot crypto chart.

        Args:
            historical: API response, list of dictionaries containing the
                historical price of a coin. Output of
                `cryptocompare.get_historical_price_*` function.
            current_price: API response, the current price of the coin. Output
                of the `cryptocompare.get_price` function.
            show: display the plot on the ePaper display.
            type: the chart type, see `mpfinance.plot`.
            **kwargs: passed to `mpfinance.plot`.

        Returns:
            The `plt.Figure` and `plt.Axes` of the plot.
        """
        df = pd.DataFrame(historical)
        df.set_index("time", inplace=True)
        df.index = pd.to_datetime(df.index, unit="s")  # type: ignore
        df.rename(
            columns={"high": "High", "close": "Close", "low": "Low", "open": "Open"},
            inplace=True,
        )
        fig, ax = self._plot()
        mpf.plot(df, type=type, ax=ax, update_width_config={"candle_linewidth": 1.5}, **kwargs)
        display_str = f"{self.coin}:{self.currency}"
        if current_price is not None:
            display_str = display_str + f" {current_price[self.coin][self.currency]}"
        text = ax.text(
            0,
            1,
            display_str,
            transform=ax.transAxes,
            fontsize=10,
            weight="bold",
            bbox=dict(boxstyle="square,pad=0", facecolor="white", edgecolor="white"),
        )
        if sub_string is not None:
            text = ax.text(
                0,
                0.88,
                sub_string,
                transform=ax.transAxes,
                fontsize=8,
                weight="bold",
                bbox=dict(
                    boxstyle="square,pad=0", facecolor="white", edgecolor="white"
                ),
            )

        fig.tight_layout(pad=0)
        if show:
            self.show_fig(fig)
        return fig, ax

    def __del__(self):
        CONFIG.module_exit()
