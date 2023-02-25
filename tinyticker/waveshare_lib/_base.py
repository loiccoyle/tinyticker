from abc import abstractmethod
from typing import Optional

from PIL import Image


class EPDBase:
    width: int
    height: int

    @abstractmethod
    def __init__(self) -> None:
        ...

    @abstractmethod
    def init(self) -> None:
        ...

    @abstractmethod
    def getbuffer(self, image: Image.Image) -> bytearray:
        ...

    @abstractmethod
    def display(self, image: bytearray) -> None:
        ...

    @abstractmethod
    def Clear() -> None:
        ...

    @abstractmethod
    def sleep() -> None:
        ...


class EPDHighlight(EPDBase):
    @abstractmethod
    def display(self, imageblack: bytearray, highlights: Optional[bytearray]) -> None:
        ...


class EPDPartial(EPDBase):
    @abstractmethod
    def displayPartial(self, image: bytearray) -> None:
        ...

    @abstractmethod
    def displayPartBaseImage(self, image: bytearray) -> None:
        ...
