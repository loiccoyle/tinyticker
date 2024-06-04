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
        self.device.module_init()

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

    def display(self, imageblack, highlights=None):
        self.send_command(0x10)
        self.send_data2(imageblack)

        if highlights is not None:
            self.send_command(0x13)
            self.send_data2(highlights)

        self.send_command(0x12)  # REFRESH
        self.ReadBusy()

    def sleep(self):
        self.send_command(0x02)  # POWER_OFF
        self.ReadBusy()
        self.send_command(0x07)  # DEEP_SLEEP
        self.send_data(0xA5)  # check code

        self.device.delay_ms(2000)
        self.device.module_exit()
