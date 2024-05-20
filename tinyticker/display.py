import logging
from typing import Optional, Tuple

import matplotlib as mpl
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import matplotlib.pyplot as plt
import mplfinance as mpf
import numpy as np
import pandas as pd
from PIL import Image

from .config import TinytickerConfig
from .waveshare_lib import MODELS
from .waveshare_lib._base import EPDHighlight

MARKETCOLORS = mpf.make_marketcolors(
    up="white",
    down="black",
    edge="black",
    wick="black",
    ohlc="black",
    volume="black",
)
MARKETCOLORS["vcedge"] = {"up": "black", "down": "black"}
STYLE = mpf.make_mpf_style(marketcolors=MARKETCOLORS, mavcolors=["k"])
STYLE_HIGHLIGHT = mpf.make_mpf_style(marketcolors=MARKETCOLORS, mavcolors=["r"])
TEXT_BBOX = {
    "boxstyle": "square,pad=0",
    "facecolor": "white",
    "edgecolor": "white",
}


class Display:
    """Display the API response on the e-Paper display.

    Args:
        model: epd model name.
        flip: Flip the display.
    """

    @classmethod
    def from_tinyticker_config(cls, tt_config: TinytickerConfig) -> "Display":
        return cls(model=tt_config.epd_model, flip=tt_config.flip)

    def __init__(
        self,
        model: str = "EPD_v2",
        flip: bool = False,
    ) -> None:
        if model not in MODELS:
            raise KeyError(
                f"Model '{model}' not found. Available models: {list(MODELS.keys())}"
            )
        self._log = logging.getLogger(__name__)
        self.flip = flip
        self.epd = MODELS[model].class_()
        self.has_highlight = isinstance(self.epd, EPDHighlight)
        self.init_epd()

    def init_epd(self):
        """Initialize the ePaper display module."""
        self._log.info("Init ePaper display.")
        self.epd.init()
        self.epd.Clear()

    @staticmethod
    def fig_to_image(fig: Figure) -> Image.Image:
        """Convert a `plt.Figure` to `PIL.Image.Image`.

        Args:
            fig: The `plt.Figure` to convert.

        Returns:
            The `PIL.Image.Image` representation of the provided `plt.Figure`.
        """
        mpl.use("Agg")
        fig.canvas.draw()
        return Image.fromarray(
            np.asarray(fig.canvas.buffer_rgba()),  # type: ignore
            mode="RGBA",
        ).convert("RGB")

    def _create_fig_ax(self, n_axes: int = 1, **kwargs) -> Tuple[Figure, np.ndarray]:
        """Create the `plt.Figure` and `plt.Axes` used to plot the chart.

        Args:
            n_axes: the number of subplot axes to create.
            **kwargs: passed to `plt.subplots`.

        Returns:
            The `plt.Figure` and an array of `plt.Axes`.
        """
        dpi = plt.rcParams.get("figure.dpi", 96)
        px = 1 / dpi
        self._log.debug("Plot width: %s", self.epd.width)
        self._log.debug("Plot height: %s", self.epd.height)
        fig, axes = plt.subplots(
            n_axes,
            1,
            figsize=(self.epd.height * px, self.epd.width * px),
            sharex=True,
            **kwargs,
        )
        if not isinstance(axes, np.ndarray):
            axes = np.array([axes])
        fig.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
        for ax in axes:
            self._strip_ax(ax)
        return fig, axes  # type: ignore

    def _strip_ax(self, ax: Axes) -> None:
        """Strip all visuals from `plt.Axes` object."""
        ax.axis(False)
        ax.margins(0, 0)
        ax.grid(False)

    def text(self, text: str, show: bool = False, **kwargs) -> Tuple[Figure, Axes]:
        """Create a `plt.Figure` and `plt.Axes` with centered text.

        Args:
            text: Text on the plot.
            show: Display the figure on the display.
            **kwargs: Passed to `ax.text`.

        Returns:
            The `plt.Figure` and `plt.Axes` with the text.
        """
        fig, ax = self._create_fig_ax(n_axes=1)
        ax = ax[0]
        ax.text(0, 0, text, ha="center", va="center", wrap=True, **kwargs)
        if show:
            self.show_fig(fig)
        return fig, ax

    def show_fig(self, fig: Figure) -> None:
        """Show a `plt.Figure` on the display."""
        image = self.fig_to_image(fig)
        self.show_image(image)

    def _show_image(
        self, image: Image.Image, highlight: Optional[Image.Image] = None
    ) -> None:
        """Small wrapper to handle the capabalities of the display."""
        if isinstance(self.epd, EPDHighlight):
            self.epd.display(
                self.epd.getbuffer(image),
                self.epd.getbuffer(highlight) if highlight is not None else None,
            )
        else:
            self.epd.display(self.epd.getbuffer(image))

    def show_image(self, image: Image.Image) -> None:
        """Show a `PIL.Image.Image` on the display.

        Args:
            image: The image to display.
        """
        highlight_image = None
        if self.has_highlight and image.mode == "RGB":
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
                "1", dither=Image.Dither.NONE
            )
            if self.flip:
                highlight_image = highlight_image.rotate(180)
            self._log.debug("Highlight image size: %s", highlight_image.size)

        if image.mode != "1":
            image = image.convert("1", dither=Image.Dither.NONE)
        if self.flip:
            image = image.rotate(180)
        self._log.debug("Image size: %s", image.size)
        self._log.info("Wake up.")
        # I think this wakes it from sleep
        self.epd.init()
        self._show_image(image, highlight_image)
        self._log.info("Display sleep.")
        self.epd.sleep()

    def plot(
        self,
        historical: pd.DataFrame,
        top_string: Optional[str] = None,
        sub_string: Optional[str] = None,
        show: bool = False,
        type: str = "candle",
        volume: bool = False,
        **kwargs,
    ) -> Tuple[Figure, Axes]:
        """Plot symbol historical data chart.

        Args:
            historical: API response, `pd.DataFrame` containing the historical
                price of the symbol.
            top_string: Contents of the top left string, '{}' will be replaced with the current
                price.
            sub_string: Contents of a smaller text box below `top_string`.
            show: display the plot on the ePaper display.
            type: the chart type, see `mplfinance.plot`.
            volume: also plot the trade volume data.
            **kwargs: passed to `mplfinance.plot`.

        Returns:
            The `plt.Figure` and `plt.Axes` of the plot.
        """
        if volume:
            fig, axes = self._create_fig_ax(
                n_axes=2, gridspec_kw={"height_ratios": [3, 1]}
            )
            volume_ax = axes[1]
        else:
            fig, axes = self._create_fig_ax(n_axes=1)
            volume_ax = False
        ax: Axes = axes[0]
        # remove Nones, it doesn't play well with mplfinance
        kwargs = {key: value for key, value in kwargs.items() if value is not None}
        mpf.plot(
            historical,
            type=type,
            ax=ax,
            update_width_config={"line_width": 1},
            style=STYLE_HIGHLIGHT if self.has_highlight else STYLE,
            volume=volume_ax,
            linecolor="k",
            **kwargs,
        )

        # Fall back to using the last closing price
        if top_string is None:
            top_string = str(historical["Close"].iloc[-1])

        ax.text(
            0,
            1,
            top_string,
            transform=ax.transAxes,
            fontsize=10,
            weight="bold",
            bbox=TEXT_BBOX,
        )
        if sub_string is not None:
            ax.text(
                0,
                0.88,
                sub_string,
                transform=ax.transAxes,
                fontsize=8,
                weight="bold",
                bbox=TEXT_BBOX,
            )

        fig.tight_layout(pad=0)
        if show:
            self.show_fig(fig)
        return fig, ax
