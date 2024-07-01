import logging

from ._base import EPDHighlight


logger = logging.getLogger(__name__)


class EPD(EPDHighlight):
    width = 104
    height = 212

    def reset(self):
        self.device.digital_write(self.reset_pin, 1)
        self.device.delay_ms(200)
        self.device.digital_write(self.reset_pin, 0)
        self.device.delay_ms(2)
        self.device.digital_write(self.reset_pin, 1)
        self.device.delay_ms(200)

    def ReadBusy(self):
        logger.debug("e-Paper busy")
        # NOTE: only 2in13b_V2 and 7in5b_V2 send 0x71 while waiting, does it do anything?
        self.send_command(0x71)
        while self.device.digital_read(self.busy_pin) == 0:
            self.send_command(0x71)
            self.device.delay_ms(100)
        logger.debug("e-Paper busy release")

    def init(self):
        self.device.module_init()

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

    def display(self, imageblack, highlights=None):
        self.send_command(0x10)
        self.send_data2(imageblack)

        if highlights is not None:
            self.send_command(0x13)
            self.send_data2(highlights)

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
