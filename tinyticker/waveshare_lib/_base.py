import logging
import math
from abc import abstractmethod
from typing import Optional, Tuple, Type

import numpy as np
from PIL import Image

from .device import RaspberryPi

logger = logging.getLogger(__name__)


class EPDBase:
    width: int
    height: int

    def __init__(self, Device: Type[RaspberryPi] = RaspberryPi) -> None:
        self.device = Device()
        self.reset_pin = self.device.RST_PIN
        self.dc_pin = self.device.DC_PIN
        self.busy_pin = self.device.BUSY_PIN
        self.cs_pin = self.device.CS_PIN
        self._blank = bytearray([0xFF] * math.ceil(self.width / 8) * self.height)

    @property
    def size(self) -> Tuple[int, int]:
        """The width and height of the display in landscape orientation."""
        # The width/height from the waveshare library are not consistent, so we wrap it in a property.
        return (
            (self.width, self.height)
            if self.width > self.height
            else (self.height, self.width)
        )

    @abstractmethod
    def init(self) -> None:
        """Initialize the display."""
        ...

    def getbuffer(self, image: Image.Image) -> bytearray:
        """Converts the given image to a buffer compatible with the EPD display.

        Args:
            image: The image to be converted.

        Returns:
            The converted buffer.

        Raises:
            ValueError: If the image dimensions are not correct.
        """
        if (self.height, self.width) == image.size:
            # image has correct dimensions, but needs to be rotated
            image = image.rotate(90, expand=True)

        if (self.width, self.height) != image.size:
            raise ValueError(
                f"Wrong image dimensions, must be {self.width}x{self.height}"
            )

        if image.mode != "1":
            image = image.convert("1", dither=Image.Dither.NONE)
        return bytearray(image.tobytes())

    def send_command(self, command: int) -> None:
        """Send command to the display.

        Args:
            command: The command to send.
        """
        self.device.digital_write(self.dc_pin, 0)
        self.device.digital_write(self.cs_pin, 0)
        self.device.spi_writebyte([command])
        self.device.digital_write(self.cs_pin, 1)

    def send_data(self, data: int) -> None:
        """Send data to the display.

        Args:
            data: The data to send.
        """
        self.device.digital_write(self.dc_pin, 1)
        self.device.digital_write(self.cs_pin, 0)
        self.device.spi_writebyte([data])
        self.device.digital_write(self.cs_pin, 1)

    def send_data2(self, data: bytearray) -> None:
        """Send a bunch of data bytes to the display.

        Args:
            data: The data to send.
        """
        self.device.digital_write(self.dc_pin, 1)
        self.device.digital_write(self.cs_pin, 0)
        self.device.spi_writebyte2(data)
        self.device.digital_write(self.cs_pin, 1)

    def sleep(self) -> None:
        """Put the display into sleep mode."""
        ...

    @abstractmethod
    def show(self, image: Image.Image) -> None:
        """Display the image on the e-paper display.

        Args:
            image: The image to display.
        """
        ...

    @abstractmethod
    def clear(self) -> None:
        """Clear the display."""
        ...


class EPDMonochrome(EPDBase):
    """EPD with only black and white color"""

    @abstractmethod
    def display(self, image: bytearray) -> None:
        """Display the image data on the e-paper display.

        Args:
            image: The image data to display.
        """
        ...

    def clear(self) -> None:
        self.display(self._blank)

    def show(self, image: Image.Image) -> None:
        self.display(self.getbuffer(image))


class EPDHighlight(EPDBase):
    """EPD with black and white color, and an extra color"""

    @abstractmethod
    def display(
        self, imageblack: bytearray, highlights: Optional[bytearray] = None
    ) -> None:
        """Display the image data on the e-paper display.

        Args:
            image: The image data to display.
            highlights: The extra color image data to display.
        """
        ...

    def clear(self) -> None:
        self.display(self._blank, highlights=self._blank)

    def show(self, image: Image.Image) -> None:
        threshold = 20
        highlight_buffer = self._blank
        if image.mode == "RGB":
            highlight_mask = np.array(image).std(axis=-1) >= threshold
            if highlight_mask.any():
                logger.info("Highlight pixels: %i", highlight_mask.sum())
                highlight_buffer = self.getbuffer(Image.fromarray(~highlight_mask))

        self.display(
            self.getbuffer(image),
            highlights=highlight_buffer,
        )


# Could be used later to utilize the partial refresh feature of some of the EPDs
# class EPDPartial(EPDBase):
#     @abstractmethod
#     def display(self, image: bytearray) -> None:
#         ...
#
#     @abstractmethod
#     def displayPartial(self, image: bytearray) -> None:
#         ...
#
#     @abstractmethod
#     def displayPartBaseImage(self, image: bytearray) -> None:
#         ...
