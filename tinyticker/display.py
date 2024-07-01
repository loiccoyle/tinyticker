"""Contains the `Display` class for displaying ticker responses on an e-Paper display.

It is basically a wrapper around the e-Paper display module, adjusting the layout's generated
image to the model's capabalities.
"""

import logging
from typing import Tuple

from matplotlib.axes import Axes
from matplotlib.figure import Figure
from PIL import Image

from .config import TinytickerConfig
from .layouts import LAYOUTS
from .layouts.utils import create_fig_ax, fig_to_image
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
        self.epd.clear()

    def text(self, text: str, show: bool = False, **kwargs) -> Tuple[Figure, Axes]:
        """Create a `plt.Figure` and `plt.Axes` with centered text.

        Args:
            text: Text on the plot.
            show: Display the figure on the display.
            **kwargs: Passed to `ax.text`.

        Returns:
            The `plt.Figure` and `plt.Axes` with the text.
        """
        fig, ax = create_fig_ax(self.epd.size, n_axes=1)
        ax = ax[0]
        ax.text(0, 0, text, ha="center", va="center", wrap=True, **kwargs)
        if show:
            self.show_fig(fig)
        return fig, ax

    def show_fig(self, fig: Figure) -> None:
        """Show a `plt.Figure` on the display."""
        image = fig_to_image(fig)
        self.show_image(image)

    def show_image(self, image: Image.Image) -> None:
        """Show a `PIL.Image.Image` on the display and put it to sleep.

        Args:
            image: The image to display.
        """
        if self.flip:
            image = image.rotate(180)

        self._log.debug("Image size: %s", image.size)
        self._log.info("Wake up.")
        self.epd.show(image)
        self._log.info("Display sleep.")
        self.epd.sleep()

    def show(self, ticker: TickerBase, resp: TickerResponse) -> None:
        layout = LAYOUTS.get(ticker.config.layout.name, LAYOUTS["default"])
        image = layout.func(self.epd.size, ticker, resp)
        self.show_image(image)
