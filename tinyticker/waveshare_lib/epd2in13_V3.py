# *****************************************************************************
# * | File        :	  epd2in13_V3.py
# * | Author      :   Waveshare team
# * | Function    :   Electronic paper driver
# * | Info        :
# *----------------
# * | This version:   V1.1
# * | Date        :   2021-10-30
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

from .epdconfig import CONFIG

# Display resolution
EPD_WIDTH = 122
EPD_HEIGHT = 250

logger = logging.getLogger(__name__)


class EPD:
    def __init__(self):
        self.reset_pin = CONFIG.RST_PIN
        self.dc_pin = CONFIG.DC_PIN
        self.busy_pin = CONFIG.BUSY_PIN
        self.cs_pin = CONFIG.CS_PIN
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT

    lut_partial_update = [
        0x0,
        0x40,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x80,
        0x80,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x40,
        0x40,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x80,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x14,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x1,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x1,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x22,
        0x22,
        0x22,
        0x22,
        0x22,
        0x22,
        0x0,
        0x0,
        0x0,
        0x22,
        0x17,
        0x41,
        0x00,
        0x32,
        0x36,
    ]

    lut_full_update = [
        0x80,
        0x4A,
        0x40,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x40,
        0x4A,
        0x80,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x80,
        0x4A,
        0x40,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x40,
        0x4A,
        0x80,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0xF,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0xF,
        0x0,
        0x0,
        0xF,
        0x0,
        0x0,
        0x2,
        0xF,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x1,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x22,
        0x22,
        0x22,
        0x22,
        0x22,
        0x22,
        0x0,
        0x0,
        0x0,
        0x22,
        0x17,
        0x41,
        0x0,
        0x32,
        0x36,
    ]

    # Hardware reset
    def reset(self):
        CONFIG.digital_write(self.reset_pin, 1)
        CONFIG.delay_ms(20)
        CONFIG.digital_write(self.reset_pin, 0)
        CONFIG.delay_ms(2)
        CONFIG.digital_write(self.reset_pin, 1)
        CONFIG.delay_ms(20)

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
        while CONFIG.digital_read(self.busy_pin) == 1:  # 0: idle, 1: busy
            CONFIG.delay_ms(10)
        logger.debug("e-Paper busy release")

    def TurnOnDisplay(self):
        self.send_command(0x22)  # Display Update Control
        self.send_data(0xC7)
        self.send_command(0x20)  # Activate Display Update Sequence
        self.ReadBusy()

    def TurnOnDisplayPart(self):
        self.send_command(0x22)  # Display Update Control
        self.send_data(0x0F)  # fast:0x0c, quality:0x0f, 0xcf
        self.send_command(0x20)  # Activate Display Update Sequence
        self.ReadBusy()

    def Lut(self, lut):
        self.send_command(0x32)
        for i in range(0, 153):
            self.send_data(lut[i])
        self.ReadBusy()

    def SetLut(self, lut):
        self.Lut(lut)
        self.send_command(0x3F)
        self.send_data(lut[153])
        self.send_command(0x03)
        # gate voltage
        self.send_data(lut[154])
        self.send_command(0x04)
        # source voltage
        self.send_data(lut[155])  # VSH
        self.send_data(lut[156])  # VSH2
        self.send_data(lut[157])  # VSL
        self.send_command(0x2C)
        # VCOM
        self.send_data(lut[158])

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

    def SetCursor(self, x, y):
        self.send_command(0x4E)  # SET_RAM_X_ADDRESS_COUNTER
        # x point must be the multiple of 8 or the last 3 bits will be ignored
        self.send_data(x & 0xFF)

        self.send_command(0x4F)  # SET_RAM_Y_ADDRESS_COUNTER
        self.send_data(y & 0xFF)
        self.send_data((y >> 8) & 0xFF)

    def init(self):
        if CONFIG.module_init() != 0:
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

        self.SetLut(self.lut_full_update)
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
            return [0x00] * (int(self.width / 8) * self.height)

        buf = bytearray(img.tobytes("raw"))
        return buf

    def display(self, image):
        if self.width % 8 == 0:
            linewidth = int(self.width / 8)
        else:
            linewidth = int(self.width / 8) + 1

        self.send_command(0x24)
        for j in range(0, self.height):
            for i in range(0, linewidth):
                self.send_data(image[i + j * linewidth])
        self.TurnOnDisplay()

    def displayPartial(self, image):
        if self.width % 8 == 0:
            linewidth = int(self.width / 8)
        else:
            linewidth = int(self.width / 8) + 1

        CONFIG.digital_write(self.reset_pin, 0)
        CONFIG.delay_ms(1)
        CONFIG.digital_write(self.reset_pin, 1)

        self.SetLut(self.lut_partial_update)
        self.send_command(0x37)
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_data(0x40)
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_data(0x00)

        self.send_command(0x3C)  # BorderWavefrom
        self.send_data(0x80)

        self.send_command(0x22)
        self.send_data(0xC0)
        self.send_command(0x20)
        self.ReadBusy()

        self.SetWindow(0, 0, self.width - 1, self.height - 1)
        self.SetCursor(0, 0)

        self.send_command(0x24)  # WRITE_RAM
        for j in range(0, self.height):
            for i in range(0, linewidth):
                self.send_data(image[i + j * linewidth])
        self.TurnOnDisplayPart()

    def displayPartBaseImage(self, image):
        if self.width % 8 == 0:
            linewidth = int(self.width / 8)
        else:
            linewidth = int(self.width / 8) + 1

        self.send_command(0x24)
        for j in range(0, self.height):
            for i in range(0, linewidth):
                self.send_data(image[i + j * linewidth])

        self.send_command(0x26)
        for j in range(0, self.height):
            for i in range(0, linewidth):
                self.send_data(image[i + j * linewidth])
        self.TurnOnDisplay()

    def Clear(self, color=0xFF):
        if self.width % 8 == 0:
            linewidth = int(self.width / 8)
        else:
            linewidth = int(self.width / 8) + 1
        # logger.debug(linewidth)

        self.send_command(0x24)
        for _ in range(0, self.height):
            for _ in range(0, linewidth):
                self.send_data(color)

        self.TurnOnDisplay()

    def sleep(self):
        self.send_command(0x10)  # enter deep sleep
        self.send_data(0x01)

        CONFIG.delay_ms(2000)
        CONFIG.module_exit()
