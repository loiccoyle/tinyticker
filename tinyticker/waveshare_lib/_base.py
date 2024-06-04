from abc import abstractmethod
from typing import Literal, Optional, Type

from PIL import Image

from .device import RaspberryPi


class EPDBase:
    width: int
    height: int

    @abstractmethod
    def __init__(self, device: Type[RaspberryPi] = RaspberryPi) -> None: ...

    @abstractmethod
    def init(self) -> Literal[0, -1]:
        """Initializes the display.

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
            raise ValueError( f"Wrong image dimensions, must be {self.width}x{self.height}")

        if image.mode != "1":
            image = image.convert("1", dither=Image.Dither.NONE)
        return bytearray(image.tobytes())

    @abstractmethod
    def Clear(self) -> None:
        """Clear the display."""
        ...

    @abstractmethod
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
