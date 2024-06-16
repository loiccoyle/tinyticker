import logging

from ._base import EPDMonochrome


logger = logging.getLogger(__name__)


class EPD(EPDMonochrome):
    width = 122
    height = 250

    def reset(self):
        self.device.digital_write(self.reset_pin, 1)
        self.device.delay_ms(20)
        self.device.digital_write(self.reset_pin, 0)
        self.device.delay_ms(2)
        self.device.digital_write(self.reset_pin, 1)
        self.device.delay_ms(20)

    def ReadBusy(self):
        logger.debug("e-Paper busy")
        while self.device.digital_read(self.busy_pin) == 1:  # 0: idle, 1: busy
            self.device.delay_ms(10)
        logger.debug("e-Paper busy release")

    def TurnOnDisplay(self):
        self.send_command(0x22)  # Display Update Control
        self.send_data(0xF7)
        self.send_command(0x20)  # Activate Display Update Sequence
        self.ReadBusy()

    def TurnOnDisplay_Fast(self):
        self.send_command(0x22)  # Display Update Control
        self.send_data(0xC7)  # fast:0x0c, quality:0x0f, 0xcf
        self.send_command(0x20)  # Activate Display Update Sequence
        self.ReadBusy()

    def TurnOnDisplayPart(self):
        self.send_command(0x22)  # Display Update Control
        self.send_data(0xFF)  # fast:0x0c, quality:0x0f, 0xcf
        self.send_command(0x20)  # Activate Display Update Sequence
        self.ReadBusy()

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
        self.device.module_init()
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

    def init_fast(self):
        self.device.module_init()
        # EPD hardware init start
        self.reset()

        self.send_command(0x12)  # SWRESET
        self.ReadBusy()

        self.send_command(0x18)  # Read built-in temperature sensor
        self.send_command(0x80)

        self.send_command(0x11)  # data entry mode
        self.send_data(0x03)

        self.SetWindow(0, 0, self.width - 1, self.height - 1)
        self.SetCursor(0, 0)

        self.send_command(0x22)  # Load temperature value
        self.send_data(0xB1)
        self.send_command(0x20)
        self.ReadBusy()

        self.send_command(0x1A)  # Write to temperature register
        self.send_data(0x64)
        self.send_data(0x00)

        self.send_command(0x22)  # Load temperature value
        self.send_data(0x91)
        self.send_command(0x20)
        self.ReadBusy()

    def display(self, image):
        self.send_command(0x24)
        self.send_data2(image)
        self.TurnOnDisplay()

    def display_fast(self, image):
        self.send_command(0x24)
        self.send_data2(image)
        self.TurnOnDisplay_Fast()

    def displayPartial(self, image):
        self.device.digital_write(self.reset_pin, 0)
        self.device.delay_ms(1)
        self.device.digital_write(self.reset_pin, 1)

        self.send_command(0x3C)  # BorderWavefrom
        self.send_data(0x80)

        self.send_command(0x01)  # Driver output control
        self.send_data(0xF9)
        self.send_data(0x00)
        self.send_data(0x00)

        self.send_command(0x11)  # data entry mode
        self.send_data(0x03)

        self.SetWindow(0, 0, self.width - 1, self.height - 1)
        self.SetCursor(0, 0)

        self.send_command(0x24)  # WRITE_RAM
        self.send_data2(image)
        self.TurnOnDisplayPart()

    def displayPartBaseImage(self, image):
        self.send_command(0x24)
        self.send_data2(image)

        self.send_command(0x26)
        self.send_data2(image)
        self.TurnOnDisplay()

    def sleep(self):
        self.send_command(0x10)  # enter deep sleep
        self.send_data(0x01)

        self.device.delay_ms(2000)
        self.device.module_exit()
