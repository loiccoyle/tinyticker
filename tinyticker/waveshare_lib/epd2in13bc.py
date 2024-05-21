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
        self.device.delay_ms(5)
        self.device.digital_write(self.reset_pin, 1)
        self.device.delay_ms(200)

    def ReadBusy(self):
        logger.debug("e-Paper busy")
        while self.device.digital_read(self.busy_pin) == 0:  # 0: idle, 1: busy
            self.device.delay_ms(100)
        logger.debug("e-Paper busy release")

    def init(self):
        if self.device.module_init() != 0:
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
        # self.send_command(0x92)

        if highlights is not None:
            self.send_command(0x13)
            for i in range(0, int(self.width * self.height / 8)):
                self.send_data(highlights[i])
            # self.send_command(0x92)

        self.send_command(0x12)  # REFRESH
        self.ReadBusy()

    def clear(self):
        self.send_command(0x10)
        for _ in range(0, int(self.width * self.height / 8)):
            self.send_data(0xFF)
        # self.send_command(0x92)

        self.send_command(0x13)
        for _ in range(0, int(self.width * self.height / 8)):
            self.send_data(0xFF)
        # self.send_command(0x92)

        self.send_command(0x12)  # REFRESH
        self.ReadBusy()

    def sleep(self):
        self.send_command(0x02)  # POWER_OFF
        self.ReadBusy()
        self.send_command(0x07)  # DEEP_SLEEP
        self.send_data(0xA5)  # check code

        self.device.delay_ms(2000)
        self.device.module_exit()
