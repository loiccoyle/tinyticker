# *****************************************************************************
# * | File        :	  epd2in13bc.py
# * | Author      :   Waveshare team
# * | Function    :   Electronic paper driver
# * | Info        :
# *----------------
# * | This version:   V4.0
# * | Date        :   2019-06-20
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

from ._base import EPDHighlight
from .epdconfig import CONFIG

# Display resolution
EPD_WIDTH = 104
EPD_HEIGHT = 212

logger = logging.getLogger(__name__)


class EPD(EPDHighlight):
    def __init__(self):
        self.reset_pin = CONFIG.RST_PIN
        self.dc_pin = CONFIG.DC_PIN
        self.busy_pin = CONFIG.BUSY_PIN
        self.cs_pin = CONFIG.CS_PIN
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT

    # Hardware reset
    def reset(self):
        CONFIG.digital_write(self.reset_pin, 1)
        CONFIG.delay_ms(200)
        CONFIG.digital_write(self.reset_pin, 0)
        CONFIG.delay_ms(5)
        CONFIG.digital_write(self.reset_pin, 1)
        CONFIG.delay_ms(200)

    def send_command(self, command):
        CONFIG.digital_write(self.dc_pin, 0)
        CONFIG.digital_write(self.cs_pin, 0)
        CONFIG.spi_writebyte([command])
        CONFIG.digital_write(self.cs_pin, 1)

    def send_data(self, data):
        CONFIG.digital_write(self.dc_pin, 1)
        CONFIG.digital_write(self.cs_pin, 0)
        CONFIG.spi_writebyte([data])
        CONFIG.digital_write(self.cs_pin, 1)

    def ReadBusy(self):
        logger.debug("e-Paper busy")
        while CONFIG.digital_read(self.busy_pin) == 0:  # 0: idle, 1: busy
            CONFIG.delay_ms(100)
        logger.debug("e-Paper busy release")

    def init(self):
        if CONFIG.module_init() != 0:
            return -1

        self.reset()

        self.send_command(0x06)  # BOOSTER_SOFT_START
        self.send_data(0x17)
        self.send_data(0x17)
        self.send_data(0x17)

        self.send_command(0x04)  # POWER_ON
        self.ReadBusy()

        self.send_command(0x00)  # PANEL_SETTING
        self.send_data(0x8F)

        self.send_command(0x50)  # VCOM_AND_DATA_INTERVAL_SETTING
        self.send_data(0xF0)

        self.send_command(0x61)  # RESOLUTION_SETTING
        self.send_data(self.width & 0xFF)
        self.send_data(self.height >> 8)
        self.send_data(self.height & 0xFF)
        return 0

    def getbuffer(self, image):
        image = image.convert("1")
        if (image.height, image.width) == (self.width, self.height):
            image = image.rotate(90, expand=True)
        if (image.height, image.width) != (self.height, self.width):
            logger.warning(
                "Wrong image dimensions: must be "
                + str(self.width)
                + "x"
                + str(self.height)
            )
            # return a blank buffer
            return bytearray([0x00] * (int(self.width / 8) * self.height))

        buf = bytearray(image.tobytes("raw"))
        return buf

    def display(self, imageblack, highlights=None):
        self.send_command(0x10)
        for i in range(0, int(self.width * self.height / 8)):
            self.send_data(imageblack[i])
        # self.send_command(0x92)

        if highlights is not None:
            self.send_command(0x13)
            for i in range(0, int(self.width * self.height / 8)):
                self.send_data(highlights[i])
            # self.send_command(0x92)

        self.send_command(0x12)  # REFRESH
        self.ReadBusy()

    def Clear(self):
        self.send_command(0x10)
        for _ in range(0, int(self.width * self.height / 8)):
            self.send_data(0xFF)
        self.send_command(0x92)

        self.send_command(0x13)
        for _ in range(0, int(self.width * self.height / 8)):
            self.send_data(0xFF)
        self.send_command(0x92)

        self.send_command(0x12)  # REFRESH
        self.ReadBusy()

    def sleep(self):
        self.send_command(0x02)  # POWER_OFF
        self.ReadBusy()
        self.send_command(0x07)  # DEEP_SLEEP
        self.send_data(0xA5)  # check code

        CONFIG.delay_ms(2000)
        CONFIG.module_exit()
