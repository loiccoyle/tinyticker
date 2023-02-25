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
        CONFIG.delay_ms(2)
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
        self.send_command(0x71)
        while CONFIG.digital_read(self.busy_pin) == 0:
            self.send_command(0x71)
            CONFIG.delay_ms(100)
        logger.debug("e-Paper busy release")

    def init(self):
        if CONFIG.module_init() != 0:
            return -1

        self.reset()
        self.send_command(0x04)
        self.ReadBusy()
        # waiting for the electronic paper IC to release the idle signal

        self.send_command(0x00)
        # panel setting
        self.send_data(0x0F)
        # LUT from OTP,128x296
        self.send_data(0x89)
        # Temperature sensor, boost and other related timing settings

        self.send_command(0x61)
        # resolution setting
        self.send_data(0x68)
        self.send_data(0x00)
        self.send_data(0xD4)

        self.send_command(0x50)
        # VCOM AND DATA INTERVAL SETTING
        self.send_data(0x77)
        # WBmode:VBDF 17|D7 VBDW 97 VBDB 57
        # WBRmode:VBDF F7 VBDW 77 VBDB 37  VBDR B7

        return 0

    def getbuffer(self, image):
        buf = [0xFF] * (int(self.width / 8) * self.height)
        image_monocolor = image.convert("1")
        imwidth, imheight = image_monocolor.size

        if imwidth == self.width and imheight == self.height:
            logger.debug("Vertical")
            for y in range(imheight):
                for x in range(imwidth):
                    # Set the bits for the column of pixels at the current position.
                    if image_monocolor.getpixel((x, y)) == 0:
                        buf[int((x + y * self.width) / 8)] &= ~(0x80 >> (x % 8))
        elif imwidth == self.height and imheight == self.width:
            logger.debug("Horizontal")
            for y in range(imheight):
                for x in range(imwidth):
                    newx = y
                    newy = self.height - x - 1
                    if image_monocolor.getpixel((x, y)) == 0:
                        buf[int((newx + newy * self.width) / 8)] &= ~(0x80 >> (y % 8))
        return buf

    def display(self, imageblack, highlights=None):
        self.send_command(0x10)
        for i in range(0, int(self.width * self.height / 8)):
            self.send_data(imageblack[i])

        if highlights is not None:
            self.send_command(0x13)
            for i in range(0, int(self.width * self.height / 8)):
                self.send_data(highlights[i])

        self.send_command(0x12)  # REFRESH
        CONFIG.delay_ms(100)
        self.ReadBusy()

    def Clear(self):
        self.send_command(0x10)
        for _ in range(0, int(self.width * self.height / 8)):
            self.send_data(0xFF)

        self.send_command(0x13)
        for _ in range(0, int(self.width * self.height / 8)):
            self.send_data(0xFF)

        self.send_command(0x12)  # REFRESH
        CONFIG.delay_ms(100)
        self.ReadBusy()

    def sleep(self):
        self.send_command(0x50)
        self.send_data(0xF7)
        self.send_command(0x02)
        self.ReadBusy()
        self.send_command(0x07)  # DEEP_SLEEP
        self.send_data(0xA5)  # check code

        CONFIG.delay_ms(2000)
        CONFIG.module_exit()
