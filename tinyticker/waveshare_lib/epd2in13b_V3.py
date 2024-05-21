import logging

from ._base import EPDHighlight


logger = logging.getLogger(__name__)


class EPD(EPDHighlight):
    width = 104
    height = 212

    # Hardware reset
    def reset(self):
        self.device.digital_write(self.reset_pin, 1)
        self.device.delay_ms(200)
        self.device.digital_write(self.reset_pin, 0)
        self.device.delay_ms(2)
        self.device.digital_write(self.reset_pin, 1)
        self.device.delay_ms(200)

    def ReadBusy(self):
        logger.debug("e-Paper busy")
        self.send_command(0x71)
        while self.device.digital_read(self.busy_pin) == 0:
            self.send_command(0x71)
            self.device.delay_ms(100)
        logger.debug("e-Paper busy release")

    def init(self):
        if self.device.module_init() != 0:
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
        return bytearray(buf)

    def display(self, imageblack, highlights=None):
        self.send_command(0x10)
        for i in range(0, int(self.width * self.height / 8)):
            self.send_data(imageblack[i])

        if highlights is not None:
            self.send_command(0x13)
            for i in range(0, int(self.width * self.height / 8)):
                self.send_data(highlights[i])

        self.send_command(0x12)  # REFRESH
        self.device.delay_ms(100)
        self.ReadBusy()

    def clear(self):
        self.send_command(0x10)
        for _ in range(0, int(self.width * self.height / 8)):
            self.send_data(0xFF)

        self.send_command(0x13)
        for _ in range(0, int(self.width * self.height / 8)):
            self.send_data(0xFF)

        self.send_command(0x12)  # REFRESH
        self.device.delay_ms(100)
        self.ReadBusy()

    def sleep(self):
        self.send_command(0x50)
        self.send_data(0xF7)
        self.send_command(0x02)
        self.ReadBusy()
        self.send_command(0x07)  # DEEP_SLEEP
        self.send_data(0xA5)  # check code

        self.device.delay_ms(2000)
        self.device.module_exit()
