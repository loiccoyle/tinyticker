# *****************************************************************************
# * | File        :	  epd2in13_V4.py
# * | Author      :   Waveshare team
# * | Function    :   Electronic paper driver
# * | Info        :
# *----------------
# * | This version:   V1.0
# * | Date        :   2023-06-25
# # | Info        :   python demo
# -----------------------------------------------------------------------------
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documnetation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to  whom the Software is
# furished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import logging
from typing import Type

from ._base import EPDMonochrome
from .device import RaspberryPi

# Display resolution
EPD_WIDTH = 122
EPD_HEIGHT = 250

logger = logging.getLogger(__name__)


class EPD(EPDMonochrome):
    def __init__(self, device: Type[RaspberryPi] = RaspberryPi):
        self.device = device()
        self.reset_pin = self.device.RST_PIN
        self.dc_pin = self.device.DC_PIN
        self.busy_pin = self.device.BUSY_PIN
        self.cs_pin = self.device.CS_PIN
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT

    """
    function :Hardware reset
    parameter:
    """

    def reset(self):
        self.device.digital_write(self.reset_pin, 1)
        self.device.delay_ms(20)
        self.device.digital_write(self.reset_pin, 0)
        self.device.delay_ms(2)
        self.device.digital_write(self.reset_pin, 1)
        self.device.delay_ms(20)

    """
    function :send command
    parameter:
     command : Command register
    """

    def send_command(self, command):
        self.device.digital_write(self.dc_pin, 0)
        self.device.digital_write(self.cs_pin, 0)
        self.device.spi_writebyte([command])
        self.device.digital_write(self.cs_pin, 1)

    """
    function :send data
    parameter:
     data : Write data
    """

    def send_data(self, data):
        self.device.digital_write(self.dc_pin, 1)
        self.device.digital_write(self.cs_pin, 0)
        self.device.spi_writebyte([data])
        self.device.digital_write(self.cs_pin, 1)

    # send a lot of data
    def send_data2(self, data):
        self.device.digital_write(self.dc_pin, 1)
        self.device.digital_write(self.cs_pin, 0)
        self.device.spi_writebyte2(data)
        self.device.digital_write(self.cs_pin, 1)

    """
    function :Wait until the busy_pin goes LOW
    parameter:
    """

    def ReadBusy(self):
        logger.debug("e-Paper busy")
        while self.device.digital_read(self.busy_pin) == 1:  # 0: idle, 1: busy
            self.device.delay_ms(10)
        logger.debug("e-Paper busy release")

    """
    function : Turn On Display
    parameter:
    """

    def TurnOnDisplay(self):
        self.send_command(0x22)  # Display Update Control
        self.send_data(0xF7)
        self.send_command(0x20)  # Activate Display Update Sequence
        self.ReadBusy()

    """
    function : Turn On Display Fast
    parameter:
    """

    # NOTE: Unused
    def TurnOnDisplay_Fast(self):
        self.send_command(0x22)  # Display Update Control
        self.send_data(0xC7)  # fast:0x0c, quality:0x0f, 0xcf
        self.send_command(0x20)  # Activate Display Update Sequence
        self.ReadBusy()

    """
    function : Turn On Display Part
    parameter:
    """

    # NOTE: Unused
    def TurnOnDisplayPart(self):
        self.send_command(0x22)  # Display Update Control
        self.send_data(0xFF)  # fast:0x0c, quality:0x0f, 0xcf
        self.send_command(0x20)  # Activate Display Update Sequence
        self.ReadBusy()

    """
    function : Setting the display window
    parameter:
        xstart : X-axis starting position
        ystart : Y-axis starting position
        xend : End position of X-axis
        yend : End position of Y-axis
    """

    def SetWindow(self, x_start, y_start, x_end, y_end):
        self.send_command(0x44)  # SET_RAM_X_ADDRESS_START_END_POSITION
        # x point must be the multiple of 8 or the last 3 bits will be ignored
        self.send_data((x_start >> 3) & 0xFF)
        self.send_data((x_end >> 3) & 0xFF)

        self.send_command(0x45)  # SET_RAM_Y_ADDRESS_START_END_POSITION
        self.send_data(y_start & 0xFF)
        self.send_data((y_start >> 8) & 0xFF)
        self.send_data(y_end & 0xFF)
        self.send_data((y_end >> 8) & 0xFF)

    """
    function : Set Cursor
    parameter:
        x : X-axis starting position
        y : Y-axis starting position
    """

    def SetCursor(self, x, y):
        self.send_command(0x4E)  # SET_RAM_X_ADDRESS_COUNTER
        # x point must be the multiple of 8 or the last 3 bits will be ignored
        self.send_data(x & 0xFF)

        self.send_command(0x4F)  # SET_RAM_Y_ADDRESS_COUNTER
        self.send_data(y & 0xFF)
        self.send_data((y >> 8) & 0xFF)

    def init(self):
        if self.device.module_init() != 0:
            return -1
        # EPD hardware init start
        self.reset()

        self.ReadBusy()
        self.send_command(0x12)  # SWRESET
        self.ReadBusy()

        self.send_command(0x01)  # Driver output control
        self.send_data(0xF9)
        self.send_data(0x00)
        self.send_data(0x00)

        self.send_command(0x11)  # data entry mode
        self.send_data(0x03)

        self.SetWindow(0, 0, self.width - 1, self.height - 1)
        self.SetCursor(0, 0)

        self.send_command(0x3C)
        self.send_data(0x05)

        self.send_command(0x21)  #  Display update control
        self.send_data(0x00)
        self.send_data(0x80)

        self.send_command(0x18)
        self.send_data(0x80)

        self.ReadBusy()

        return 0

    """
    function : Initialize the e-Paper fast register
    parameter:
    """

    # NOTE: Unused
    def init_fast(self):
        if self.device.module_init() != 0:
            return -1
        # EPD hardware init start
        self.reset()

        self.send_command(0x12)  # SWRESET
        self.ReadBusy()

        self.send_command(0x18)  # Read built-in temperature sensor
        self.send_command(0x80)

        self.send_command(0x11)  # data entry mode
        self.send_data(0x03)

        self.SetWindow(0, 0, self.width - 1, self.height - 1)
        self.SetCursor(0, 0)

        self.send_command(0x22)  # Load temperature value
        self.send_data(0xB1)
        self.send_command(0x20)
        self.ReadBusy()

        self.send_command(0x1A)  # Write to temperature register
        self.send_data(0x64)
        self.send_data(0x00)

        self.send_command(0x22)  # Load temperature value
        self.send_data(0x91)
        self.send_command(0x20)
        self.ReadBusy()

        return 0

    def display(self, image):
        self.send_command(0x24)
        self.send_data2(image)
        self.TurnOnDisplay()

    """
    function : Sends the image buffer in RAM to e-Paper and fast displays
    parameter:
        image : Image data
    """

    # NOTE: Unused
    def display_fast(self, image):
        self.send_command(0x24)
        self.send_data2(image)
        self.TurnOnDisplay_Fast()

    """
    function : Sends the image buffer in RAM to e-Paper and partial refresh
    parameter:
        image : Image data
    """

    # NOTE: Unused
    def displayPartial(self, image):
        self.device.digital_write(self.reset_pin, 0)
        self.device.delay_ms(1)
        self.device.digital_write(self.reset_pin, 1)

        self.send_command(0x3C)  # BorderWavefrom
        self.send_data(0x80)

        self.send_command(0x01)  # Driver output control
        self.send_data(0xF9)
        self.send_data(0x00)
        self.send_data(0x00)

        self.send_command(0x11)  # data entry mode
        self.send_data(0x03)

        self.SetWindow(0, 0, self.width - 1, self.height - 1)
        self.SetCursor(0, 0)

        self.send_command(0x24)  # WRITE_RAM
        self.send_data2(image)
        self.TurnOnDisplayPart()

    """
    function : Refresh a base image
    parameter:
        image : Image data
    """

    # NOTE: Unused
    def displayPartBaseImage(self, image):
        self.send_command(0x24)
        self.send_data2(image)

        self.send_command(0x26)
        self.send_data2(image)
        self.TurnOnDisplay()

    def Clear(self, color=0xFF):
        if self.width % 8 == 0:
            linewidth = int(self.width / 8)
        else:
            linewidth = int(self.width / 8) + 1
        # logger.debug(linewidth)

        self.send_command(0x24)
        self.send_data2([color] * int(self.height * linewidth))
        self.TurnOnDisplay()

    def sleep(self):
        self.send_command(0x10)  # enter deep sleep
        self.send_data(0x01)

        self.device.delay_ms(2000)
        self.device.module_exit()
