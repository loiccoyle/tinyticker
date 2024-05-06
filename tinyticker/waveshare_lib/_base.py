from abc import abstractmethod
from typing import Literal, Optional

from PIL import Image


class EPDBase:
    width: int
    height: int

    @abstractmethod
    def __init__(self) -> None: ...

    @abstractmethod
    def init(self) -> Literal[0, -1]:
        """Initializes the display.

        Returns:
            The initialization status. It can be either 0 or -1.
        """
        ...

    @abstractmethod
    def getbuffer(self, image: Image.Image) -> bytearray:
        """Converts the given image to a buffer compatible with the EPD display.

        Args:
            image: The image to be converted.

        Returns:
            The converted buffer.
        """
        ...

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
    def display(self, imageblack: bytearray, highlights: Optional[bytearray]) -> None:
        """Displays the given image on the e-paper display.

        Args:
            image: The image data to display.
            highlights: The highlight data to display.
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
