from abc import abstractmethod
from typing import Literal, Optional

from PIL import Image


class EPDBase:
    width: int
    height: int

    @abstractmethod
    def __init__(self) -> None:
        ...

    @abstractmethod
    def init(self) -> Literal[0, -1]:
        ...

    @abstractmethod
    def getbuffer(self, image: Image.Image) -> bytearray:
        ...

    @abstractmethod
    def Clear(self) -> None:
        ...

    @abstractmethod
    def sleep(self) -> None:
        ...


class EPDMonochrome(EPDBase):
    """EPD with only black and white color"""

    @abstractmethod
    def display(self, image: bytearray) -> None:
        ...


class EPDHighlight(EPDBase):
    """EPD with black and white color, and an extra color"""

    @abstractmethod
    def display(self, imageblack: bytearray, highlights: Optional[bytearray]) -> None:
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
