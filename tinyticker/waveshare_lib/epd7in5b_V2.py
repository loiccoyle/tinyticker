import logging

from ._base import EPDHighlight

logger = logging.getLogger(__name__)


class EPD(EPDHighlight):
    width = 800
    height = 480

    # Hardware reset
    def reset(self):
        self.device.digital_write(self.reset_pin, 1)
        self.device.delay_ms(200)
        self.device.digital_write(self.reset_pin, 0)
        self.device.delay_ms(4)
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

    def display(self, imageblack, highlights=None):
        self.send_command(0x10)
        self.send_data2(imageblack)

        if highlights is not None:
            self.send_command(0x13)
            self.send_data2(highlights)

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
