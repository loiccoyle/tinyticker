# *****************************************************************************
# * | File        :	  epd7in5.py
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
from typing import Type

from ._base import EPDMonochrome
from .device import RaspberryPi

# Display resolution
EPD_WIDTH = 800
EPD_HEIGHT = 480

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

    # Hardware reset
    def reset(self):
        self.device.digital_write(self.reset_pin, 1)
        self.device.delay_ms(20)
        self.device.digital_write(self.reset_pin, 0)
        self.device.delay_ms(2)
        self.device.digital_write(self.reset_pin, 1)
        self.device.delay_ms(20)

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

    def send_data2(self, data):
        self.device.digital_write(self.dc_pin, 1)
        self.device.digital_write(self.cs_pin, 0)
        self.device.SPI.writebytes2(data)
        self.device.digital_write(self.cs_pin, 1)

    def ReadBusy(self):
        logger.debug("e-Paper busy")
        self.send_command(0x71)
        busy = self.device.digital_read(self.busy_pin)
        while busy == 0:
            self.send_command(0x71)
            busy = self.device.digital_read(self.busy_pin)
        self.device.delay_ms(20)
        logger.debug("e-Paper busy release")

    def init(self):
        if self.device.module_init() != 0:
            return -1
        # EPD hardware init start
        self.reset()

        self.send_command(0x06)  # btst
        self.send_data(0x17)
        self.send_data(0x17)
        self.send_data(0x28)  # If an exception is displayed, try using 0x38
        self.send_data(0x17)

        self.send_command(0x01)  # POWER SETTING
        self.send_data(0x07)
        self.send_data(0x07)  # VGH=20V,VGL=-20V
        self.send_data(0x3F)  # VDH=15V
        self.send_data(0x3F)  # VDL=-15V

        self.send_command(0x04)  # POWER ON
        self.device.delay_ms(100)
        self.ReadBusy()

        self.send_command(0x00)  # PANNEL SETTING
        self.send_data(0x1F)  # KW-3f   KWR-2F	BWROTP 0f	BWOTP 1f

        self.send_command(0x61)  # tres
        self.send_data(0x03)  # source 800
        self.send_data(0x20)
        self.send_data(0x01)  # gate 480
        self.send_data(0xE0)

        self.send_command(0x15)
        self.send_data(0x00)

        self.send_command(0x50)  # VCOM AND DATA INTERVAL SETTING
        self.send_data(0x10)
        self.send_data(0x07)

        self.send_command(0x60)  # TCON SETTING
        self.send_data(0x22)

        # EPD hardware init end
        return 0

    def init_fast(self):
        if self.device.module_init() != 0:
            return -1
        # EPD hardware init start
        self.reset()

        self.send_command(0x00)  # PANNEL SETTING
        self.send_data(0x1F)  # KW-3f   KWR-2F	BWROTP 0f	BWOTP 1f

        self.send_command(0x50)  # VCOM AND DATA INTERVAL SETTING
        self.send_data(0x10)
        self.send_data(0x07)

        self.send_command(0x04)  # POWER ON
        self.device.delay_ms(100)
        self.ReadBusy()  # waiting for the electronic paper IC to release the idle signal

        # Enhanced display drive(Add 0x06 command)
        self.send_command(0x06)  # Booster Soft Start
        self.send_data(0x27)
        self.send_data(0x27)
        self.send_data(0x18)
        self.send_data(0x17)

        self.send_command(0xE0)
        self.send_data(0x02)
        self.send_command(0xE5)
        self.send_data(0x5A)

        # EPD hardware init end
        return 0

    def init_part(self):
        if self.device.module_init() != 0:
            return -1
        # EPD hardware init start
        self.reset()

        self.send_command(0x00)  # PANNEL SETTING
        self.send_data(0x1F)  # KW-3f   KWR-2F	BWROTP 0f	BWOTP 1f

        self.send_command(0x04)  # POWER ON
        self.device.delay_ms(100)
        self.ReadBusy()  # waiting for the electronic paper IC to release the idle signal

        self.send_command(0xE0)
        self.send_data(0x02)
        self.send_command(0xE5)
        self.send_data(0x6E)

        # EPD hardware init end
        return 0

    def getbuffer(self, image):
        img = image
        imwidth, imheight = img.size
        if imwidth == self.width and imheight == self.height:
            img = img.convert("1")
        elif imwidth == self.height and imheight == self.width:
            # image has correct dimensions, but needs to be rotated
            img = img.rotate(90, expand=True).convert("1")
        else:
            logger.warning(
                "Wrong image dimensions: must be "
                + str(self.width)
                + "x"
                + str(self.height)
            )
            # return a blank buffer
            return bytearray([0x00] * (int(self.width / 8) * self.height))

        buf = bytearray(img.tobytes("raw"))
        # The bytes need to be inverted, because in the PIL world 0=black and 1=white, but
        # in the e-paper world 0=white and 1=black.
        for i in range(len(buf)):
            buf[i] ^= 0xFF
        return buf

    def display(self, image):
        if self.width % 8 == 0:
            Width = self.width // 8
        else:
            Width = self.width // 8 + 1
        Height = self.height
        image1 = [0xFF] * int(self.width * self.height / 8)
        for j in range(Height):
            for i in range(Width):
                image1[i + j * Width] = ~image[i + j * Width]
        self.send_command(0x10)
        self.send_data2(image1)

        self.send_command(0x13)
        self.send_data2(image)

        self.send_command(0x12)
        self.device.delay_ms(100)
        self.ReadBusy()

    def Clear(self):
        self.send_command(0x10)
        self.send_data2([0xFF] * int(self.width * self.height / 8))
        self.send_command(0x13)
        self.send_data2([0x00] * int(self.width * self.height / 8))

        self.send_command(0x12)
        self.device.delay_ms(100)
        self.ReadBusy()

    def display_Partial(self, Image, Xstart, Ystart, Xend, Yend):
        if (
            (Xstart % 8 + Xend % 8 == 8 & Xstart % 8 > Xend % 8) | Xstart % 8 + Xend % 8
            == 0 | (Xend - Xstart) % 8
            == 0
        ):
            Xstart = Xstart // 8 * 8
            Xend = Xend // 8 * 8
        else:
            Xstart = Xstart // 8 * 8
            if Xend % 8 == 0:
                Xend = Xend // 8 * 8
            else:
                Xend = Xend // 8 * 8 + 1

        Width = (Xend - Xstart) // 8
        Height = Yend - Ystart

        self.send_command(0x50)
        self.send_data(0xA9)
        self.send_data(0x07)

        self.send_command(0x91)  # This command makes the display enter partial mode
        self.send_command(0x90)  # resolution setting
        self.send_data(Xstart // 256)
        self.send_data(Xstart % 256)  # x-start

        self.send_data((Xend - 1) // 256)
        self.send_data((Xend - 1) % 256)  # x-end

        self.send_data(Ystart // 256)  #
        self.send_data(Ystart % 256)  # y-start

        self.send_data((Yend - 1) // 256)
        self.send_data((Yend - 1) % 256)  # y-end
        self.send_data(0x01)

        image1 = [0xFF] * int(self.width * self.height / 8)
        for j in range(Height):
            for i in range(Width):
                image1[i + j * Width] = ~Image[i + j * Width]

        self.send_command(0x13)  # Write Black and White image to RAM
        self.send_data2(image1)

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
