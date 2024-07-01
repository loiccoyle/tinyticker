import logging

from ._base import EPDGrayscale

logger = logging.getLogger(__name__)


class EPD(EPDGrayscale):
    width = 176
    height = 264

    LUT_DATA_4Gray = [
        0x40,
        0x48,
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
        0x8,
        0x48,
        0x10,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x2,
        0x48,
        0x4,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x20,
        0x48,
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
        0xA,
        0x19,
        0x0,
        0x3,
        0x8,
        0x0,
        0x0,
        0x14,
        0x1,
        0x0,
        0x14,
        0x1,
        0x0,
        0x3,
        0xA,
        0x3,
        0x0,
        0x8,
        0x19,
        0x0,
        0x0,
        0x1,
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
        0x1C,
    ]

    def reset(self):
        self.device.digital_write(self.reset_pin, 1)
        self.device.delay_ms(200)
        self.device.digital_write(self.reset_pin, 0)
        self.device.delay_ms(2)
        self.device.digital_write(self.reset_pin, 1)
        self.device.delay_ms(200)

    def ReadBusy(self):
        logger.debug("e-Paper busy")
        while self.device.digital_read(self.busy_pin) == 1:  #  1: idle, 0: busy
            self.device.delay_ms(20)
        logger.debug("e-Paper busy release")

    def TurnOnDisplay(self):
        self.send_command(0x22)  # Display Update Control
        self.send_data(0xF7)
        self.send_command(0x20)  # Activate Display Update Sequence
        self.ReadBusy()

    def TurnOnDisplay_Fast(self):
        self.send_command(0x22)  # Display Update Control
        self.send_data(0xC7)
        self.send_command(0x20)  # Activate Display Update Sequence
        self.ReadBusy()

    def TurnOnDisplay_Partial(self):
        self.send_command(0x22)  # Display Update Control
        self.send_data(0xFF)
        self.send_command(0x20)  # Activate Display Update Sequence
        self.ReadBusy()

    def TurnOnDisplay_4GRAY(self):
        self.send_command(0x22)  # Display Update Control
        self.send_data(0xC7)
        self.send_command(0x20)  # Activate Display Update Sequence
        self.ReadBusy()

    def Lut(self):
        self.send_command(0x32)
        for i in range(159):
            self.send_data(self.LUT_DATA_4Gray[i])

    def init(self):
        self.device.module_init()

        # EPD hardware init start
        self.reset()
        self.ReadBusy()

        self.send_command(0x12)  # SWRESET
        self.ReadBusy()

        self.send_command(0x45)  # set Ram-Y address start/end position
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_data(0x07)  # 0x0107-->(263+1)=264
        self.send_data(0x01)

        self.send_command(0x4F)  # set RAM y address count to 0;
        self.send_data(0x00)
        self.send_data(0x00)

        self.send_command(0x11)  # data entry mode
        self.send_data(0x03)

    def init_Fast(self):
        self.device.module_init()

        # EPD hardware init start
        self.reset()
        self.ReadBusy()

        self.send_command(0x12)  # SWRESET
        self.ReadBusy()

        self.send_command(0x12)  # SWRESET
        self.ReadBusy()

        self.send_command(0x18)  # Read built-in temperature sensor
        self.send_data(0x80)

        self.send_command(0x22)  # Load temperature value
        self.send_data(0xB1)
        self.send_command(0x20)
        self.ReadBusy()

        self.send_command(0x1A)  # Write to temperature register
        self.send_data(0x64)
        self.send_data(0x00)

        self.send_command(0x45)  # set Ram-Y address start/end position
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_data(0x07)  # 0x0107-->(263+1)=264
        self.send_data(0x01)

        self.send_command(0x4F)  # set RAM y address count to 0;
        self.send_data(0x00)
        self.send_data(0x00)

        self.send_command(0x11)  # data entry mode
        self.send_data(0x03)

        self.send_command(0x22)  # Load temperature value
        self.send_data(0x91)
        self.send_command(0x20)
        self.ReadBusy()

    def init_grayscale(self):
        self.device.module_init()

        self.reset()

        self.send_command(0x12)  # soft reset
        self.ReadBusy()
        self.send_command(0x74)  # set analog block control
        self.send_data(0x54)
        self.send_command(0x7E)  # set digital block control
        self.send_data(0x3B)

        self.send_command(0x01)  # Driver output control
        self.send_data(0x07)
        self.send_data(0x01)
        self.send_data(0x00)

        self.send_command(0x11)  # data entry mode
        self.send_data(0x03)

        self.send_command(0x44)  # set Ram-X address start/end position
        self.send_data(0x00)
        self.send_data(0x15)  # 0x15-->(21+1)*8=176

        self.send_command(0x45)  # set Ram-Y address start/end position
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_data(0x07)  # 0x0107-->(263+1)=264
        self.send_data(0x01)

        self.send_command(0x3C)  # BorderWavefrom
        self.send_data(0x00)

        self.send_command(0x2C)  # VCOM Voltage
        self.send_data(self.LUT_DATA_4Gray[158])  # 0x1C

        self.send_command(0x3F)  # EOPQ
        self.send_data(self.LUT_DATA_4Gray[153])

        self.send_command(0x03)  # VGH
        self.send_data(self.LUT_DATA_4Gray[154])

        self.send_command(0x04)  #
        self.send_data(self.LUT_DATA_4Gray[155])  # VSH1
        self.send_data(self.LUT_DATA_4Gray[156])  # VSH2
        self.send_data(self.LUT_DATA_4Gray[157])  # VSL

        self.Lut()  # LUT

        self.send_command(0x4E)  # set RAM x address count to 0;
        self.send_data(0x00)
        self.send_command(0x4F)  # set RAM y address count to 0X199;
        self.send_data(0x00)
        self.send_data(0x00)
        self.ReadBusy()

    def display(self, image):
        self.send_command(0x24)
        self.send_data2(image)
        self.TurnOnDisplay()

    def display_Fast(self, image):
        self.send_command(0x24)
        self.send_data2(image)
        self.TurnOnDisplay_Fast()

    def display_Base(self, image):
        if self.width % 8 == 0:
            Width = self.width // 8
        else:
            Width = self.width // 8 + 1
        Height = self.height
        self.send_command(0x24)  # Write Black and White image to RAM
        for j in range(Height):
            for i in range(Width):
                self.send_data(image[i + j * Width])

        self.send_command(0x26)  # Write Black and White image to RAM
        for j in range(Height):
            for i in range(Width):
                self.send_data(image[i + j * Width])
        self.TurnOnDisplay()

    def display_Base_color(self, color):
        if self.width % 8 == 0:
            Width = self.width // 8
        else:
            Width = self.width // 8 + 1
        Height = self.height
        self.send_command(0x24)  # Write Black and White image to RAM
        for _ in range(Height):
            for _ in range(Width):
                self.send_data(color)

        self.send_command(0x26)  # Write Black and White image to RAM
        for _ in range(Height):
            for _ in range(Width):
                self.send_data(color)
        # self.TurnOnDisplay()

    def display_Partial(self, Image, Xstart, Ystart, Xend, Yend):
        if (
            (Xstart % 8 + Xend % 8 == 8 & Xstart % 8 > Xend % 8) | Xstart % 8 + Xend % 8
            == 0 | (Xend - Xstart) % 8
            == 0
        ):
            Xstart = Xstart // 8
            Xend = Xend // 8
        else:
            Xstart = Xstart // 8
            if Xend % 8 == 0:
                Xend = Xend // 8
            else:
                Xend = Xend // 8 + 1

        if self.width % 8 == 0:
            Width = self.width // 8
        else:
            Width = self.width // 8 + 1
        Height = self.height

        Xend -= 1
        Yend -= 1

        # Reset
        self.reset()

        self.send_command(0x3C)  # BorderWavefrom
        self.send_data(0x80)

        self.send_command(0x44)  # set RAM x address start/end, in page 35
        self.send_data(Xstart & 0xFF)  # RAM x address start at 00h;
        self.send_data(Xend & 0xFF)  # RAM x address end at 0fh(15+1)*8->128
        self.send_command(0x45)  # set RAM y address start/end, in page 35
        self.send_data(Ystart & 0xFF)  # RAM y address start at 0127h;
        self.send_data((Ystart >> 8) & 0x01)  # RAM y address start at 0127h;
        self.send_data(Yend & 0xFF)  # RAM y address end at 00h;
        self.send_data((Yend >> 8) & 0x01)

        self.send_command(0x4E)  # set RAM x address count to 0;
        self.send_data(Xstart & 0xFF)
        self.send_command(0x4F)  # set RAM y address count to 0X127;
        self.send_data(Ystart & 0xFF)
        self.send_data((Ystart >> 8) & 0x01)

        self.send_command(0x24)  # Write Black and White image to RAM
        for j in range(Height):
            for i in range(Width):
                if (
                    (j > Ystart - 1)
                    & (j < (Yend + 1))
                    & (i > Xstart - 1)
                    & (i < (Xend + 1))
                ):
                    self.send_data(Image[i + j * Width])
        self.TurnOnDisplay_Partial()

    def display_grayscale(self, image):
        self.send_command(0x24)
        for i in range(0, 5808):  # 5808*4  46464
            temp3 = 0
            for j in range(0, 2):
                temp1 = image[i * 2 + j]
                for k in range(0, 2):
                    temp2 = temp1 & 0xC0
                    if temp2 == 0xC0:
                        temp3 |= 0x00
                    elif temp2 == 0x00:
                        temp3 |= 0x01
                    elif temp2 == 0x80:
                        temp3 |= 0x01
                    else:  # 0x40
                        temp3 |= 0x00
                    temp3 <<= 1

                    temp1 <<= 2
                    temp2 = temp1 & 0xC0
                    if temp2 == 0xC0:
                        temp3 |= 0x00
                    elif temp2 == 0x00:
                        temp3 |= 0x01
                    elif temp2 == 0x80:
                        temp3 |= 0x01
                    else:  # 0x40
                        temp3 |= 0x00
                    if j != 1 or k != 1:
                        temp3 <<= 1
                    temp1 <<= 2
            self.send_data(temp3)

        self.send_command(0x26)
        for i in range(0, 5808):  # 5808*4  46464
            temp3 = 0
            for j in range(0, 2):
                temp1 = image[i * 2 + j]
                for k in range(0, 2):
                    temp2 = temp1 & 0xC0
                    if temp2 == 0xC0:
                        temp3 |= 0x00
                    elif temp2 == 0x00:
                        temp3 |= 0x01
                    elif temp2 == 0x80:
                        temp3 |= 0x00
                    else:  # 0x40
                        temp3 |= 0x01
                    temp3 <<= 1

                    temp1 <<= 2
                    temp2 = temp1 & 0xC0
                    if temp2 == 0xC0:
                        temp3 |= 0x00
                    elif temp2 == 0x00:
                        temp3 |= 0x01
                    elif temp2 == 0x80:
                        temp3 |= 0x00
                    else:  # 0x40
                        temp3 |= 0x01
                    if j != 1 or k != 1:
                        temp3 <<= 1
                    temp1 <<= 2
            self.send_data(temp3)

        self.TurnOnDisplay_4GRAY()

    def sleep(self):
        self.send_command(0x10)
        self.send_data(0x01)

        self.device.delay_ms(2000)
        self.device.module_exit()
