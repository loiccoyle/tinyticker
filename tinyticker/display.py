"""Contains the `Display` class for displaying ticker responses on an e-Paper display.

It is basically a wrapper around the e-Paper display module, adjusting the layout's generated
image to the model's capabalities.
"""

import logging
from typing import Optional, Tuple

import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from PIL import Image

from .config import TinytickerConfig
from .layouts import LAYOUTS, _create_fig_ax, _fig_to_image
from .tickers._base import TickerBase, TickerResponse
from .waveshare_lib._base import EPDHighlight
from .waveshare_lib.models import MODELS, EPDModel


class Display:
    """Display the ticker response on the e-Paper display.

    Args:
        epd: e-Paper display model.
        flip: Flip the display.
    """

    @classmethod
    def from_tinyticker_config(cls, tt_config: TinytickerConfig) -> "Display":
        """Create a `Display` object from a `TinytickerConfig` object."""
        epd = MODELS[tt_config.epd_model].EPD()
        return cls(epd, flip=tt_config.flip)

    def __init__(
        self,
        epd: EPDModel,
        flip: bool = False,
    ) -> None:
        self._log = logging.getLogger(__name__)
        self.flip = flip
        self.epd = epd
        self.has_highlight = isinstance(self.epd, EPDHighlight)
        self.init_epd()

    def init_epd(self):
        """Initialize the ePaper display module."""
        self._log.info("Init ePaper display.")
        self.epd.init()
        self.epd.Clear()

    def text(self, text: str, show: bool = False, **kwargs) -> Tuple[Figure, Axes]:
        """Create a `plt.Figure` and `plt.Axes` with centered text.

        Args:
            text: Text on the plot.
            show: Display the figure on the display.
            **kwargs: Passed to `ax.text`.

        Returns:
            The `plt.Figure` and `plt.Axes` with the text.
        """
        fig, ax = _create_fig_ax((self.epd.height, self.epd.width), n_axes=1)
        ax = ax[0]
        ax.text(0, 0, text, ha="center", va="center", wrap=True, **kwargs)
        if show:
            self.show_fig(fig)
        return fig, ax

    def show_fig(self, fig: Figure) -> None:
        """Show a `plt.Figure` on the display."""
        image = _fig_to_image(fig)
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
        """Show a `PIL.Image.Image` on the display and put it to sleep.

        Args:
            image: The image to display.
        """
        if self.flip:
            image = image.rotate(180)

        highlight_image = None
        if self.has_highlight and image.mode == "RGB":
            self._log.info("Computing highlight pixels.")
            # create an image with the red pixels
            image_ar = np.array(image)
            red_pixels = (image_ar[:, :, 0] > 127) & (image_ar[:, :, 1:] < 127).all(
                axis=-1
            )
            n_red = red_pixels.sum()
            if n_red > 0:
                highlight_image = (
                    np.ones(image_ar.shape[:-1], dtype=image_ar.dtype) * 255
                )
                self._log.debug("Number of red pixels: %s", n_red)
                highlight_image[red_pixels] = 0
                # I think there is a bug with PIL, need to convert from "L"
                # https://stackoverflow.com/questions/32159076/python-pil-bitmap-png-from-array-with-mode-1
                highlight_image = Image.fromarray(highlight_image, mode="L")
                self._log.debug("Highlight image size: %s", highlight_image.size)

        self._log.debug("Image size: %s", image.size)
        self._log.info("Wake up.")
        # I think this wakes it from sleep
        self.epd.init()
        self._show_image(image, highlight_image)
        self._log.info("Display sleep.")
        self.epd.sleep()

    def show(self, ticker: TickerBase, resp: TickerResponse) -> None:
        layout = LAYOUTS.get(ticker.config.layout.name, LAYOUTS["default"])
        image = layout.func((self.epd.height, self.epd.width), ticker, resp)
        self.show_image(image)
