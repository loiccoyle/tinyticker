from abc import abstractmethod
from typing import Literal, Optional, Type

from PIL import Image

from .device import RaspberryPi


class EPDBase:
    width: int
    height: int

    @abstractmethod
    def __init__(self, device: Type[RaspberryPi] = RaspberryPi) -> None:
        self.device = device()
        self.reset_pin = self.device.RST_PIN
        self.dc_pin = self.device.DC_PIN
        self.busy_pin = self.device.BUSY_PIN
        self.cs_pin = self.device.CS_PIN

    @abstractmethod
    def init(self) -> Literal[0, -1]:
        """Initialize the display.

        Returns:
            The initialization status. It can be either 0 or -1.
        """
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
                "Wrong image dimensions, must be %sx%s", self.width, self.height
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

    @abstractmethod
    def clear(self) -> None:
        """Clear the display."""
        ...

    def sleep(self) -> None:
        """Put the display into sleep mode."""
        ...


class EPDMonochrome(EPDBase):
    """EPD with only black and white color"""

    @abstractmethod
    def display(self, image: bytearray) -> None:
        """Displays the given image on the e-paper display.

        Args:
            image: The image data to display.
        """
        ...


class EPDHighlight(EPDBase):
    """EPD with black and white color, and an extra color"""

    @abstractmethod
    def display(
        self, imageblack: bytearray, highlights: Optional[bytearray] = None
    ) -> None:
        """Displays the given image on the e-paper display.

        Args:
            image: The image data to display.
            highlights: The extra color image data to display.
        """
        ...


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
