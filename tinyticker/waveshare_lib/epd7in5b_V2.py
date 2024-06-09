# *****************************************************************************
# * | File        :	  epd7in5b_V2.py
# * | Author      :   Waveshare team
# * | Function    :   Electronic paper driver
# * | Info        :
# *----------------
# * | This version:   V4.2
# * | Date        :   2022-01-08
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

from ._base import EPDHighlight
from .device import RaspberryPi

# Display resolution
EPD_WIDTH = 800
EPD_HEIGHT = 480

logger = logging.getLogger(__name__)


class EPD(EPDHighlight):
    def __init__(self, device: Type[RaspberryPi] = RaspberryPi):
        self.device = device()
        self.reset_pin = self.device.RST_PIN
        self.dc_pin = self.device.DC_PIN
        self.busy_pin = self.device.BUSY_PIN
        self.cs_pin = self.device.CS_PIN
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT

    # Hardware reset
    def reset(self):
        self.device.digital_write(self.reset_pin, 1)
        self.device.delay_ms(200)
        self.device.digital_write(self.reset_pin, 0)
        self.device.delay_ms(4)
        self.device.digital_write(self.reset_pin, 1)
        self.device.delay_ms(200)

    def send_command(self, command):
        self.device.digital_write(self.dc_pin, 0)
        self.device.digital_write(self.cs_pin, 0)
        self.device.spi_writebyte([command])
        self.device.digital_write(self.cs_pin, 1)

    def send_data(self, data):
        self.device.digital_write(self.dc_pin, 1)
        self.device.digital_write(self.cs_pin, 0)
        self.device.spi_writebyte([data])
        self.device.digital_write(self.cs_pin, 1)

    def send_data2(self, data):  # faster
        self.device.digital_write(self.dc_pin, 1)
        self.device.digital_write(self.cs_pin, 0)
        self.device.spi_writebyte2(data)
        self.device.digital_write(self.cs_pin, 1)

    def ReadBusy(self):
        logger.debug("e-Paper busy")
        self.send_command(0x71)
        busy = self.device.digital_read(self.busy_pin)
        while busy == 0:
            self.send_command(0x71)
            busy = self.device.digital_read(self.busy_pin)
        self.device.delay_ms(200)
        logger.debug("e-Paper busy release")

    def init(self):
        if self.device.module_init() != 0:
            return -1

        self.reset()

        # self.send_command(0x06)   # btst
        # self.send_data(0x17)
        # self.send_data(0x17)
        # self.send_data(0x38)      # If an exception is displayed, try using 0x38
        # self.send_data(0x17)

        self.send_command(0x01)  # POWER SETTING
        self.send_data(0x07)
        self.send_data(0x07)  # VGH=20V,VGL=-20V
        self.send_data(0x3F)  # VDH=15V
        self.send_data(0x3F)  # VDL=-15V

        self.send_command(0x04)  # POWER ON
        self.device.delay_ms(100)
        self.ReadBusy()

        self.send_command(0x00)  # PANNEL SETTING
        self.send_data(0x0F)  # KW-3f KWR-2F BWROTP-0f BWOTP-1f

        self.send_command(0x61)  # tres
        self.send_data(0x03)  # source 800
        self.send_data(0x20)
        self.send_data(0x01)  # gate 480
        self.send_data(0xE0)

        self.send_command(0x15)
        self.send_data(0x00)

        self.send_command(0x50)  # VCOM AND DATA INTERVAL SETTING
        self.send_data(0x11)
        self.send_data(0x07)

        self.send_command(0x60)  # TCON SETTING
        self.send_data(0x22)

        self.send_command(0x65)
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_data(0x00)

        return 0

    def display(self, imageblack, highlights=None):
        self.send_command(0x10)
        self.send_data2(imageblack)

        if highlights is not None:
            self.send_command(0x13)
            self.send_data2(highlights)

        self.send_command(0x12)
        self.device.delay_ms(100)
        self.ReadBusy()

    def Clear(self):
        buf = [0x00] * (int(self.width / 8) * self.height)
        buf2 = [0xFF] * (int(self.width / 8) * self.height)
        self.send_command(0x10)
        self.send_data2(buf2)

        self.send_command(0x13)
        self.send_data2(buf)

        self.send_command(0x12)
        self.device.delay_ms(100)
        self.ReadBusy()

    def sleep(self):
        self.send_command(0x02)  # POWER_OFF
        self.ReadBusy()

        self.send_command(0x07)  # DEEP_SLEEP
        self.send_data(0xA5)

        self.device.delay_ms(2000)
        self.device.module_exit()
