import logging

from ._base import EPDHighlight


logger = logging.getLogger(__name__)


class EPD(EPDHighlight):
    width = 122
    height = 250

    # hardware reset
    def reset(self):
        self.device.digital_write(self.reset_pin, 1)
        self.device.delay_ms(20)
        self.device.digital_write(self.reset_pin, 0)
        self.device.delay_ms(2)
        self.device.digital_write(self.reset_pin, 1)
        self.device.delay_ms(20)

    # judge e-Paper whether is ReadBusy
    def ReadBusy(self):
        logger.debug("e-Paper busy")
        while self.device.digital_read(self.busy_pin) != 0:
            self.device.delay_ms(10)
        logger.debug("e-Paper busy release")

    # set the display window
    def set_windows(self, xstart, ystart, xend, yend):
        self.send_command(0x44)  # SET_RAM_X_ADDRESS_START_END_POSITION
        self.send_data((xstart >> 3) & 0xFF)
        self.send_data((xend >> 3) & 0xFF)

        self.send_command(0x45)  # SET_RAM_Y_ADDRESS_START_END_POSITION
        self.send_data(ystart & 0xFF)
        self.send_data((ystart >> 8) & 0xFF)
        self.send_data(yend & 0xFF)
        self.send_data((yend >> 8) & 0xFF)

    # set the display cursor(origin)
    def set_cursor(self, xstart, ystart):
        self.send_command(0x4E)  # SET_RAM_X_ADDRESS_COUNTER
        self.send_data(xstart & 0xFF)

        self.send_command(0x4F)  # SET_RAM_Y_ADDRESS_COUNTER
        self.send_data(ystart & 0xFF)
        self.send_data((ystart >> 8) & 0xFF)

    # initialize
    def init(self):
        if self.device.module_init() != 0:
            return -1

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

        self.set_windows(0, 0, self.width - 1, self.height - 1)
        self.set_cursor(0, 0)

        self.send_command(0x3C)  # BorderWavefrom
        self.send_data(0x05)

        self.send_command(0x18)  # Read built-in temperature sensor
        self.send_data(0x80)

        self.send_command(0x21)  # Display update control
        self.send_data(0x80)
        self.send_data(0x80)

        self.ReadBusy()

        return 0

    # turn on display
    def TurnOnDisplay(self):
        self.send_command(0x20)
        self.ReadBusy()

    # display image
    def display(self, imageblack, highlights=None):
        self.send_command(0x24)
        self.send_data2(imageblack)

        if highlights is not None:
            self.send_command(0x26)
            self.send_data2(highlights)

        self.TurnOnDisplay()

    # display white image
    def clear(self):
        if self.width % 8 == 0:
            linewidth = int(self.width / 8)
        else:
            linewidth = int(self.width / 8) + 1

        buf = [0xFF] * (int(linewidth * self.height))

        self.send_command(0x24)
        self.send_data2(buf)

        self.send_command(0x26)
        self.send_data2(buf)

        self.TurnOnDisplay()

    # sleep
    def sleep(self):
        self.send_command(0x10)  # DEEP_SLEEP
        self.send_data(0x01)  # check code

        self.device.delay_ms(2000)
        self.device.module_exit()
