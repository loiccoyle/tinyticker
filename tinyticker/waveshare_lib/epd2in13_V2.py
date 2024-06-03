import logging

from ._base import EPDMonochrome

logger = logging.getLogger(__name__)

FULL_UPDATE = 0


class EPD(EPDMonochrome):
    width = 122
    height = 250
    lut_full_update = [
        0x80,
        0x60,
        0x40,
        0x00,
        0x00,
        0x00,
        0x00,  # LUT0: BB:     VS 0 ~7
        0x10,
        0x60,
        0x20,
        0x00,
        0x00,
        0x00,
        0x00,  # LUT1: BW:     VS 0 ~7
        0x80,
        0x60,
        0x40,
        0x00,
        0x00,
        0x00,
        0x00,  # LUT2: WB:     VS 0 ~7
        0x10,
        0x60,
        0x20,
        0x00,
        0x00,
        0x00,
        0x00,  # LUT3: WW:     VS 0 ~7
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,  # LUT4: VCOM:   VS 0 ~7
        0x03,
        0x03,
        0x00,
        0x00,
        0x02,  # TP0 A~D RP0
        0x09,
        0x09,
        0x00,
        0x00,
        0x02,  # TP1 A~D RP1
        0x03,
        0x03,
        0x00,
        0x00,
        0x02,  # TP2 A~D RP2
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,  # TP3 A~D RP3
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,  # TP4 A~D RP4
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,  # TP5 A~D RP5
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,  # TP6 A~D RP6
        0x15,
        0x41,
        0xA8,
        0x32,
        0x30,
        0x0A,
    ]

    lut_partial_update = [  # 20 bytes
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,  # LUT0: BB:     VS 0 ~7
        0x80,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,  # LUT1: BW:     VS 0 ~7
        0x40,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,  # LUT2: WB:     VS 0 ~7
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,  # LUT3: WW:     VS 0 ~7
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,  # LUT4: VCOM:   VS 0 ~7
        0x0A,
        0x00,
        0x00,
        0x00,
        0x00,  # TP0 A~D RP0
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,  # TP1 A~D RP1
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,  # TP2 A~D RP2
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,  # TP3 A~D RP3
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,  # TP4 A~D RP4
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,  # TP5 A~D RP5
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,  # TP6 A~D RP6
        0x15,
        0x41,
        0xA8,
        0x32,
        0x30,
        0x0A,
    ]

    # Hardware reset
    def reset(self):
        self.device.digital_write(self.reset_pin, 1)
        self.device.delay_ms(200)
        self.device.digital_write(self.reset_pin, 0)
        self.device.delay_ms(5)
        self.device.digital_write(self.reset_pin, 1)
        self.device.delay_ms(200)

    # send a lot of data
    def send_data2(self, data):
        self.device.digital_write(self.dc_pin, 1)
        self.device.digital_write(self.cs_pin, 0)
        self.device.spi_writebyte2(data)
        self.device.digital_write(self.cs_pin, 1)

    def ReadBusy(self):
        while self.device.digital_read(self.busy_pin) == 1:  # 0: idle, 1: busy
            self.device.delay_ms(100)

    def TurnOnDisplay(self):
        self.send_command(0x22)
        self.send_data(0xC7)
        self.send_command(0x20)
        self.ReadBusy()

    # NOTE: unused
    def TurnOnDisplayPart(self):
        self.send_command(0x22)
        self.send_data(0x0C)
        self.send_command(0x20)
        self.ReadBusy()

    def init(self, update=FULL_UPDATE):
        if self.device.module_init() != 0:
            return -1
        # EPD hardware init start
        self.reset()
        if update == FULL_UPDATE:
            self.ReadBusy()
            self.send_command(0x12)  # soft reset
            self.ReadBusy()

            self.send_command(0x74)  # set analog block control
            self.send_data(0x54)
            self.send_command(0x7E)  # set digital block control
            self.send_data(0x3B)

            self.send_command(0x01)  # Driver output control
            self.send_data(0xF9)
            self.send_data(0x00)
            self.send_data(0x00)

            self.send_command(0x11)  # data entry mode
            self.send_data(0x01)

            self.send_command(0x44)  # set Ram-X address start/end position
            self.send_data(0x00)
            self.send_data(0x0F)  # 0x0C-->(15+1)*8=128

            self.send_command(0x45)  # set Ram-Y address start/end position
            self.send_data(0xF9)  # 0xF9-->(249+1)=250
            self.send_data(0x00)
            self.send_data(0x00)
            self.send_data(0x00)

            self.send_command(0x3C)  # BorderWavefrom
            self.send_data(0x03)

            self.send_command(0x2C)  # VCOM Voltage
            self.send_data(0x55)  #

            self.send_command(0x03)
            self.send_data(self.lut_full_update[70])

            self.send_command(0x04)  #
            self.send_data(self.lut_full_update[71])
            self.send_data(self.lut_full_update[72])
            self.send_data(self.lut_full_update[73])

            self.send_command(0x3A)  # Dummy Line
            self.send_data(self.lut_full_update[74])
            self.send_command(0x3B)  # Gate time
            self.send_data(self.lut_full_update[75])

            self.send_command(0x32)
            for count in range(70):
                self.send_data(self.lut_full_update[count])

            self.send_command(0x4E)  # set RAM x address count to 0
            self.send_data(0x00)
            self.send_command(0x4F)  # set RAM y address count to 0X127
            self.send_data(0xF9)
            self.send_data(0x00)
            self.ReadBusy()
        else:
            self.send_command(0x2C)  # VCOM Voltage
            self.send_data(0x26)

            self.ReadBusy()

            self.send_command(0x32)
            for count in range(70):
                self.send_data(self.lut_partial_update[count])

            self.send_command(0x37)
            self.send_data(0x00)
            self.send_data(0x00)
            self.send_data(0x00)
            self.send_data(0x00)
            self.send_data(0x40)
            self.send_data(0x00)
            self.send_data(0x00)

            self.send_command(0x22)
            self.send_data(0xC0)
            self.send_command(0x20)
            self.ReadBusy()

            self.send_command(0x3C)  # BorderWavefrom
            self.send_data(0x01)
        return 0

    def display(self, image):
        self.send_command(0x24)
        self.send_data2(image)
        self.TurnOnDisplay()

    # NOTE: unused
    def displayPartial(self, image):
        if self.width % 8 == 0:
            linewidth = int(self.width / 8)
        else:
            linewidth = int(self.width / 8) + 1

        buf = [0x00] * self.height * linewidth
        for j in range(0, self.height):
            for i in range(0, linewidth):
                buf[i + j * linewidth] = ~image[i + j * linewidth]

        self.send_command(0x24)
        self.send_data2(image)

        self.send_command(0x26)
        self.send_data2(buf)
        self.TurnOnDisplayPart()

    # NOTE: unused
    def displayPartBaseImage(self, image):
        self.send_command(0x24)
        self.send_data2(image)

        self.send_command(0x26)
        self.send_data2(image)
        self.TurnOnDisplay()

    def clear(self, color=0xFF):
        if self.width % 8 == 0:
            linewidth = int(self.width / 8)
        else:
            linewidth = int(self.width / 8) + 1
        # logger.debug(linewidth)

        buf = [0x00] * self.height * linewidth
        for j in range(0, self.height):
            for i in range(0, linewidth):
                buf[i + j * linewidth] = color

        self.send_command(0x24)
        self.send_data2(buf)

        # self.send_command(0x26)
        # for j in range(0, self.height):
        # for i in range(0, linewidth):
        # self.send_data(color)

        self.TurnOnDisplay()

    def sleep(self):
        # self.send_command(0x22) #POWER OFF
        # self.send_data(0xC3)
        # self.send_command(0x20)

        self.send_command(0x10)  # enter deep sleep
        self.send_data(0x03)
        self.device.delay_ms(2000)
        self.device.module_exit()
