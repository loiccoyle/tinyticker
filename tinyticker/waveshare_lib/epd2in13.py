import logging

from ._base import EPDMonochrome

logger = logging.getLogger(__name__)


class EPD(EPDMonochrome):
    width = 122
    height = 250
    lut_full_update = [
        0x22,
        0x55,
        0xAA,
        0x55,
        0xAA,
        0x55,
        0xAA,
        0x11,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x1E,
        0x1E,
        0x1E,
        0x1E,
        0x1E,
        0x1E,
        0x1E,
        0x1E,
        0x01,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
    ]

    def reset(self):
        self.device.digital_write(self.reset_pin, 1)
        self.device.delay_ms(200)
        self.device.digital_write(self.reset_pin, 0)
        self.device.delay_ms(5)
        self.device.digital_write(self.reset_pin, 1)
        self.device.delay_ms(200)

    def ReadBusy(self):
        logger.debug("e-Paper busy")
        while self.device.digital_read(self.busy_pin) == 1:  # 0: idle, 1: busy
            self.device.delay_ms(100)
        logger.debug("e-Paper busy release")

    def TurnOnDisplay(self):
        self.send_command(0x22)  # DISPLAY_UPDATE_CONTROL_2
        self.send_data(0xC4)
        self.send_command(0x20)  # MASTER_ACTIVATION
        self.send_command(0xFF)  # TERMINATE_FRAME_READ_WRITE

        logger.debug("e-Paper busy")
        self.ReadBusy()
        logger.debug("e-Paper busy release")

    def init(self):
        self.device.module_init()
        # EPD hardware init start
        self.reset()
        self.send_command(0x01)  # DRIVER_OUTPUT_CONTROL
        self.send_data((self.height - 1) & 0xFF)
        self.send_data(((self.height - 1) >> 8) & 0xFF)
        self.send_data(0x00)  # GD = 0 SM = 0 TB = 0

        self.send_command(0x0C)  # BOOSTER_SOFT_START_CONTROL
        self.send_data(0xD7)
        self.send_data(0xD6)
        self.send_data(0x9D)

        self.send_command(0x2C)  # WRITE_VCOM_REGISTER
        self.send_data(0xA8)  # VCOM 7C

        self.send_command(0x3A)  # SET_DUMMY_LINE_PERIOD
        self.send_data(0x1A)  # 4 dummy lines per gate

        self.send_command(0x3B)  # SET_GATE_TIME
        self.send_data(0x08)  # 2us per line

        self.send_command(0x3C)  # BORDER_WAVEFORM_CONTROL
        self.send_data(0x03)

        self.send_command(0x11)  # DATA_ENTRY_MODE_SETTING
        self.send_data(0x03)  # X increment; Y increment

        # WRITE_LUT_REGISTER
        self.send_command(0x32)
        for count in range(30):
            self.send_data(self.lut_full_update[count])

    def SetWindows(self, x_start, y_start, x_end, y_end):
        self.send_command(0x44)  # SET_RAM_X_ADDRESS_START_END_POSITION
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
        self.send_data((x >> 3) & 0xFF)
        self.send_command(0x4F)  # SET_RAM_Y_ADDRESS_COUNTER
        self.send_data(y & 0xFF)
        self.send_data((y >> 8) & 0xFF)
        self.ReadBusy()

    def display(self, image):
        if self.width % 8 == 0:
            linewidth = int(self.width / 8)
        else:
            linewidth = int(self.width / 8) + 1

        self.SetWindows(0, 0, self.width, self.height)
        for j in range(0, self.height):
            self.SetCursor(0, j)
            self.send_command(0x24)
            for i in range(0, linewidth):
                self.send_data(image[i + j * linewidth])
        self.TurnOnDisplay()

    def sleep(self):
        self.send_command(0x10)  # enter deep sleep
        self.send_data(0x01)
        self.device.delay_ms(2000)
        self.device.module_exit()
