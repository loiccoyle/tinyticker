from abc import abstractmethod
from typing import Literal, Optional, List, Union

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
    def getbuffer(
        self, image: Image.Image
    ) -> Union[
        bytearray, List[int]
    ]:  # some implementations return a list of ints, some a bytearray...
        ...

    @abstractmethod
    def Clear(self) -> None:
        ...

    @abstractmethod
    def sleep(self) -> None:
        ...


class EPDHighlight(EPDBase):
    @abstractmethod
    def display(self, imageblack: bytearray, highlights: Optional[bytearray]) -> None:
        ...


class EPDPartial(EPDBase):
    @abstractmethod
    def display(self, image: bytearray) -> None:
        ...

    @abstractmethod
    def displayPartial(self, image: bytearray) -> None:
        ...

    @abstractmethod
    def displayPartBaseImage(self, image: bytearray) -> None:
        ...
