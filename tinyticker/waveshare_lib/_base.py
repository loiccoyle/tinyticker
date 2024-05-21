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
    def init(self) -> Literal[0, -1]: ...

    def send_command(self, command: int) -> None:
        """Send command to the e-Paper.

        Args:
            command: The command to send.
        """
        self.device.digital_write(self.dc_pin, 0)
        self.device.digital_write(self.cs_pin, 0)
        self.device.spi_writebyte([command])
        self.device.digital_write(self.cs_pin, 1)

    def send_data(self, data: int) -> None:
        """Send data to the e-Paper.

        Args:
            data: The data to send.
        """
        self.device.digital_write(self.dc_pin, 1)
        self.device.digital_write(self.cs_pin, 0)
        self.device.spi_writebyte([data])
        self.device.digital_write(self.cs_pin, 1)

    @abstractmethod
    def getbuffer(self, image: Image.Image) -> bytearray: ...

    @abstractmethod
    def clear(self) -> None: ...

    @abstractmethod
    def sleep(self) -> None: ...


class EPDMonochrome(EPDBase):
    """EPD with only black and white color"""

    @abstractmethod
    def display(self, image: bytearray) -> None: ...


class EPDHighlight(EPDBase):
    """EPD with black and white color, and an extra color"""

    @abstractmethod
    def display(
        self, imageblack: bytearray, highlights: Optional[bytearray]
    ) -> None: ...


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
