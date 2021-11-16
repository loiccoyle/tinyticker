import logging
from typing import Optional, Tuple

import matplotlib
import matplotlib.pyplot as plt
import mplfinance as mpf
import numpy as np
import pandas as pd
from PIL import Image

from .waveshare_lib import CONFIG
from .waveshare_lib.models import MODELS


class Display:
    """Handle the displaying of the API response.

    Args:
        flip: Flip the display.
    """

    def __init__(
        self,
        model: str = "EPD_v2",
        flip: bool = False,
    ) -> None:
        self._log = logging.getLogger(__name__)
        self.previous_response = {}
        self.flip = flip
        self.model = MODELS[model]
        self.epd = self.model.class_()
        self.init_epd()

    def init_epd(self):
        """Initialize the ePaper display module."""
        self._log.info("Init ePaper display.")
        self.epd.init()
        self.epd.Clear()

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

    def _create_fig_ax(self) -> Tuple[plt.Figure, plt.Axes]:
        """Create the matplotlib figure and axes used to plot the chart."""
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

    def text(
        self, text: str, show: bool = False, **kwargs
    ) -> Tuple[plt.Figure, plt.Axes]:
        """Create a plt.Figure, plt.Axes with text centered.

        Args:
            text: Text on the plot.
            show: Display the figure on the display.
            **kwargs: Passed to `ax.text`.

        Returns:
            The `plt.Figure` and `plt.Axes` with the text.
        """
        fig, ax = self._create_fig_ax()
        ax.text(0, 0, text, ha="center", va="center", wrap=True, **kwargs)
        if show:
            self.show_fig(fig)
        return fig, ax

    def show_fig(self, fig: plt.Figure) -> None:
        """Show a `plt.Figure` on the display."""
        image = self.fig_to_image(fig)
        self.show_image(image)

    def show_image(self, image: Image.Image) -> None:
        """Show a `PIL.Image.Image` on the display."""
        highlight_image = None
        if self.model.has_highlight and image.mode == "RGB":
            self._log.info("Computing highlight pixels.")
            # create an image with the pixels which are coloured
            image_ar = np.array(image)
            colored_pixels = ~(image_ar == image_ar[:, :, 0][:, :, None]).all(axis=-1)
            highlight_image = np.ones(image_ar.shape[:-1], dtype=image_ar.dtype) * 255
            self._log.debug("Number of coloured pixels: %s", colored_pixels.sum())
            highlight_image[colored_pixels] = 0
            # I think there is a bug with PIL, need to convert from "L"
            # https://stackoverflow.com/questions/32159076/python-pil-bitmap-png-from-array-with-mode-1
            highlight_image = Image.fromarray(highlight_image, mode="L").convert(
                "1", dither=Image.NONE
            )
            if self.flip:
                highlight_image = highlight_image.rotate(180)
            self._log.debug("Highlight image size: %s", highlight_image.size)

        if image.mode != "1":
            image = image.convert("1", dither=Image.NONE)
        if self.flip:
            image = image.rotate(180)
        self._log.debug("Image size: %s", image.size)
        self._log.info("Wake up.")
        # I think this wakes it from sleep
        self.epd.init()
        if highlight_image is not None:
            self.epd.display(
                self.epd.getbuffer(image),
                self.epd.getbuffer(highlight_image),
            )
        else:
            self.epd.display(self.epd.getbuffer(image))
        self._log.info("Display sleep.")
        self.epd.sleep()

    def plot(
        self,
        historical: pd.DataFrame,
        current_price: Optional[float],
        top_string: Optional[str] = None,
        sub_string: Optional[str] = None,
        show: bool = False,
        type: str = "candle",
        **kwargs,
    ) -> Tuple[plt.Figure, plt.Axes]:
        """Plot symbol chart.

        Args:
            historical: API response, `pd.DataFrame` containing the historical
                price of the symbol.
            current_price: API response, the current price of the symbol.
            top_string: Contents of the top left string, the current will be
                appended if provided.
            sub_string: Contents of a smaller text box bollow top_string.
            show: display the plot on the ePaper display.
            type: the chart type, see `mpfinance.plot`.
            **kwargs: passed to `mpfinance.plot`.

        Returns:
            The `plt.Figure` and `plt.Axes` of the plot.
        """
        fig, ax = self._create_fig_ax()
        marketcolors = mpf.make_marketcolors(
            up="white", down="k", edge="k", wick="k", ohlc="k"
        )
        if self.model.has_highlight:
            mavcolors = ["r"]
        else:
            mavcolors = ["k"]
        s = mpf.make_mpf_style(marketcolors=marketcolors, mavcolors=mavcolors)
        # remove Nones, it doesn't play well with mplfinance
        kwargs = {key: value for key, value in kwargs.items() if value is not None}
        mpf.plot(
            historical,
            type=type,
            ax=ax,
            update_width_config={"line_width": 1},
            style=s,
            **kwargs,
        )
        # Fall back to using the last closing price
        if current_price is None:
            current_price = historical.iloc[-1]["Close"]
        if top_string is not None:
            top_string += f" {current_price:.2f}"
        else:
            top_string = str(current_price)
        if top_string is not None:
            ax.text(
                0,
                1,
                top_string,
                transform=ax.transAxes,
                fontsize=10,
                weight="bold",
                bbox=dict(
                    boxstyle="square,pad=0",
                    facecolor="white",
                    edgecolor="white",
                ),
            )
        if sub_string is not None:
            ax.text(
                0,
                0.88,
                sub_string,
                transform=ax.transAxes,
                fontsize=8,
                weight="bold",
                bbox=dict(
                    boxstyle="square,pad=0",
                    facecolor="white",
                    edgecolor="white",
                ),
            )

        fig.tight_layout(pad=0)
        ax.grid(False)
        if show:
            self.show_fig(fig)
        return fig, ax

    def __del__(self):
        try:
            CONFIG.module_exit()
        except Exception:
            pass
