import logging

from ._base import EPDGrayscale

logger = logging.getLogger(__name__)


class EPD(EPDGrayscale):
    width = 176
    height = 264

    lut_vcom_dc = [
        0x00,
        0x00,
        0x00,
        0x08,
        0x00,
        0x00,
        0x00,
        0x02,
        0x60,
        0x28,
        0x28,
        0x00,
        0x00,
        0x01,
        0x00,
        0x14,
        0x00,
        0x00,
        0x00,
        0x01,
        0x00,
        0x12,
        0x12,
        0x00,
        0x00,
        0x01,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
    ]
    lut_ww = [
        0x40,
        0x08,
        0x00,
        0x00,
        0x00,
        0x02,
        0x90,
        0x28,
        0x28,
        0x00,
        0x00,
        0x01,
        0x40,
        0x14,
        0x00,
        0x00,
        0x00,
        0x01,
        0xA0,
        0x12,
        0x12,
        0x00,
        0x00,
        0x01,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
    ]
    lut_bw = [
        0x40,
        0x08,
        0x00,
        0x00,
        0x00,
        0x02,
        0x90,
        0x28,
        0x28,
        0x00,
        0x00,
        0x01,
        0x40,
        0x14,
        0x00,
        0x00,
        0x00,
        0x01,
        0xA0,
        0x12,
        0x12,
        0x00,
        0x00,
        0x01,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
    ]
    lut_bb = [
        0x80,
        0x08,
        0x00,
        0x00,
        0x00,
        0x02,
        0x90,
        0x28,
        0x28,
        0x00,
        0x00,
        0x01,
        0x80,
        0x14,
        0x00,
        0x00,
        0x00,
        0x01,
        0x50,
        0x12,
        0x12,
        0x00,
        0x00,
        0x01,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
    ]
    lut_wb = [
        0x80,
        0x08,
        0x00,
        0x00,
        0x00,
        0x02,
        0x90,
        0x28,
        0x28,
        0x00,
        0x00,
        0x01,
        0x80,
        0x14,
        0x00,
        0x00,
        0x00,
        0x01,
        0x50,
        0x12,
        0x12,
        0x00,
        0x00,
        0x01,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
    ]
    ###################full screen update LUT######################
    # 0~3 gray
    gray_lut_vcom = [
        0x00,
        0x00,
        0x00,
        0x0A,
        0x00,
        0x00,
        0x00,
        0x01,
        0x60,
        0x14,
        0x14,
        0x00,
        0x00,
        0x01,
        0x00,
        0x14,
        0x00,
        0x00,
        0x00,
        0x01,
        0x00,
        0x13,
        0x0A,
        0x01,
        0x00,
        0x01,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
    ]
    # R21
    gray_lut_ww = [
        0x40,
        0x0A,
        0x00,
        0x00,
        0x00,
        0x01,
        0x90,
        0x14,
        0x14,
        0x00,
        0x00,
        0x01,
        0x10,
        0x14,
        0x0A,
        0x00,
        0x00,
        0x01,
        0xA0,
        0x13,
        0x01,
        0x00,
        0x00,
        0x01,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
    ]
    # R22H	r
    gray_lut_bw = [
        0x40,
        0x0A,
        0x00,
        0x00,
        0x00,
        0x01,
        0x90,
        0x14,
        0x14,
        0x00,
        0x00,
        0x01,
        0x00,
        0x14,
        0x0A,
        0x00,
        0x00,
        0x01,
        0x99,
        0x0C,
        0x01,
        0x03,
        0x04,
        0x01,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
    ]
    # R23H	w
    gray_lut_wb = [
        0x40,
        0x0A,
        0x00,
        0x00,
        0x00,
        0x01,
        0x90,
        0x14,
        0x14,
        0x00,
        0x00,
        0x01,
        0x00,
        0x14,
        0x0A,
        0x00,
        0x00,
        0x01,
        0x99,
        0x0B,
        0x04,
        0x04,
        0x01,
        0x01,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
    ]
    # R24H	b
    gray_lut_bb = [
        0x80,
        0x0A,
        0x00,
        0x00,
        0x00,
        0x01,
        0x90,
        0x14,
        0x14,
        0x00,
        0x00,
        0x01,
        0x20,
        0x14,
        0x0A,
        0x00,
        0x00,
        0x01,
        0x50,
        0x13,
        0x01,
        0x00,
        0x00,
        0x01,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
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
        while self.device.digital_read(self.busy_pin) == 0:  #  0: idle, 1: busy
            self.device.delay_ms(200)
        logger.debug("e-Paper busy release")

    def set_lut(self):
        self.send_command(0x20)  # vcom
        for count in range(0, 44):
            self.send_data(self.lut_vcom_dc[count])
        self.send_command(0x21)  # ww --
        for count in range(0, 42):
            self.send_data(self.lut_ww[count])
        self.send_command(0x22)  # bw r
        for count in range(0, 42):
            self.send_data(self.lut_bw[count])
        self.send_command(0x23)  # wb w
        for count in range(0, 42):
            self.send_data(self.lut_bb[count])
        self.send_command(0x24)  # bb b
        for count in range(0, 42):
            self.send_data(self.lut_wb[count])

    def gray_SetLut(self):
        self.send_command(0x20)
        for count in range(0, 44):  # vcom
            self.send_data(self.gray_lut_vcom[count])

        self.send_command(0x21)  # red not use
        for count in range(0, 42):
            self.send_data(self.gray_lut_ww[count])

        self.send_command(0x22)  # bw r
        for count in range(0, 42):
            self.send_data(self.gray_lut_bw[count])

        self.send_command(0x23)  # wb w
        for count in range(0, 42):
            self.send_data(self.gray_lut_wb[count])

        self.send_command(0x24)  # bb b
        for count in range(0, 42):
            self.send_data(self.gray_lut_bb[count])

        self.send_command(0x25)  # vcom
        for count in range(0, 42):
            self.send_data(self.gray_lut_ww[count])

    def init(self):
        self.device.module_init()

        # EPD hardware init start
        self.reset()

        self.send_command(0x01)  # POWER_SETTING
        self.send_data(0x03)  # VDS_EN, VDG_EN
        self.send_data(0x00)  # VCOM_HV, VGHL_LV[1], VGHL_LV[0]
        self.send_data(0x2B)  # VDH
        self.send_data(0x2B)  # VDL
        self.send_data(0x09)  # VDHR

        self.send_command(0x06)  # BOOSTER_SOFT_START
        self.send_data(0x07)
        self.send_data(0x07)
        self.send_data(0x17)

        # Power optimization
        self.send_command(0xF8)
        self.send_data(0x60)
        self.send_data(0xA5)

        # Power optimization
        self.send_command(0xF8)
        self.send_data(0x89)
        self.send_data(0xA5)

        # Power optimization
        self.send_command(0xF8)
        self.send_data(0x90)
        self.send_data(0x00)

        # Power optimization
        self.send_command(0xF8)
        self.send_data(0x93)
        self.send_data(0x2A)

        # Power optimization
        self.send_command(0xF8)
        self.send_data(0xA0)
        self.send_data(0xA5)

        # Power optimization
        self.send_command(0xF8)
        self.send_data(0xA1)
        self.send_data(0x00)

        # Power optimization
        self.send_command(0xF8)
        self.send_data(0x73)
        self.send_data(0x41)

        self.send_command(0x16)  # PARTIAL_DISPLAY_REFRESH
        self.send_data(0x00)
        self.send_command(0x04)  # POWER_ON
        self.ReadBusy()

        self.send_command(0x00)  # PANEL_SETTING
        self.send_data(0xAF)  # KW-BF   KWR-AF    BWROTP 0f

        self.send_command(0x30)  # PLL_CONTROL
        self.send_data(0x3A)  # 3A 100HZ   29 150Hz 39 200HZ    31 171HZ

        self.send_command(0x50)  # VCOM AND DATA INTERVAL SETTING
        self.send_data(0x57)

        self.send_command(0x82)  # VCM_DC_SETTING_REGISTER
        self.send_data(0x12)
        self.set_lut()

    def init_grayscale(self):
        self.device.module_init()

        self.reset()

        self.send_command(0x01)  # POWER SETTING
        self.send_data(0x03)
        self.send_data(0x00)
        self.send_data(0x2B)
        self.send_data(0x2B)

        self.send_command(0x06)  # booster soft start
        self.send_data(0x07)  # A
        self.send_data(0x07)  # B
        self.send_data(0x17)  # C

        self.send_command(0xF8)  # boost??
        self.send_data(0x60)
        self.send_data(0xA5)

        self.send_command(0xF8)  # boost??
        self.send_data(0x89)
        self.send_data(0xA5)

        self.send_command(0xF8)  # boost??
        self.send_data(0x90)
        self.send_data(0x00)

        self.send_command(0xF8)  # boost??
        self.send_data(0x93)
        self.send_data(0x2A)

        self.send_command(0xF8)  # boost??
        self.send_data(0xA0)
        self.send_data(0xA5)

        self.send_command(0xF8)  # boost??
        self.send_data(0xA1)
        self.send_data(0x00)

        self.send_command(0xF8)  # boost??
        self.send_data(0x73)
        self.send_data(0x41)

        self.send_command(0x16)
        self.send_data(0x00)

        self.send_command(0x04)
        self.ReadBusy()

        self.send_command(0x00)  # panel setting
        self.send_data(0xBF)  # KW-BF   KWR-AF	BWROTP 0f

        self.send_command(0x30)  # PLL setting
        self.send_data(0x90)  # 100hz

        self.send_command(0x61)  # resolution setting
        self.send_data(0x00)  # 176
        self.send_data(0xB0)
        self.send_data(0x01)  # 264
        self.send_data(0x08)

        self.send_command(0x82)  # vcom_DC setting
        self.send_data(0x12)

        self.send_command(0x50)  # VCOM AND DATA INTERVAL SETTING
        self.send_data(0x57)

    def display(self, image):
        self.send_command(0x13)
        self.send_data2(image)
        self.send_command(0x12)
        self.ReadBusy()

    def display_grayscale(self, image):
        self.send_command(0x10)
        for i in range(0, 5808):  # 5808*4  46464
            temp3 = 0
            for j in range(0, 2):
                temp1 = image[i * 2 + j]
                for k in range(0, 2):
                    temp2 = temp1 & 0xC0
                    if temp2 == 0xC0:
                        temp3 |= 0x01  # white
                    elif temp2 == 0x00:
                        temp3 |= 0x00  # black
                    elif temp2 == 0x80:
                        temp3 |= 0x01  # gray1
                    else:  # 0x40
                        temp3 |= 0x00  # gray2
                    temp3 <<= 1

                    temp1 <<= 2
                    temp2 = temp1 & 0xC0
                    if temp2 == 0xC0:  # white
                        temp3 |= 0x01
                    elif temp2 == 0x00:  # black
                        temp3 |= 0x00
                    elif temp2 == 0x80:
                        temp3 |= 0x01  # gray1
                    else:  # 0x40
                        temp3 |= 0x00  # gray2
                    if j != 1 or k != 1:
                        temp3 <<= 1
                    temp1 <<= 2
            self.send_data(temp3)

        self.send_command(0x13)
        for i in range(0, 5808):  # 5808*4  46464
            temp3 = 0
            for j in range(0, 2):
                temp1 = image[i * 2 + j]
                for k in range(0, 2):
                    temp2 = temp1 & 0xC0
                    if temp2 == 0xC0:
                        temp3 |= 0x01  # white
                    elif temp2 == 0x00:
                        temp3 |= 0x00  # black
                    elif temp2 == 0x80:
                        temp3 |= 0x00  # gray1
                    else:  # 0x40
                        temp3 |= 0x01  # gray2
                    temp3 <<= 1

                    temp1 <<= 2
                    temp2 = temp1 & 0xC0
                    if temp2 == 0xC0:  # white
                        temp3 |= 0x01
                    elif temp2 == 0x00:  # black
                        temp3 |= 0x00
                    elif temp2 == 0x80:
                        temp3 |= 0x00  # gray1
                    else:  # 0x40
                        temp3 |= 0x01  # gray2
                    if j != 1 or k != 1:
                        temp3 <<= 1
                    temp1 <<= 2
            self.send_data(temp3)

        self.gray_SetLut()
        self.send_command(0x12)
        self.device.delay_ms(200)
        self.ReadBusy()

    def clear(self):
        # NOTE: for this display we also clear the gray layer, for some reason in the V2
        # it isn't done, so I don't know if it is actually needed here...
        # if it isn't needed then we can use the base class' `clear` implementation and rm this
        self.send_command(0x10)
        self.send_data2(self._blank)
        self.display(self._blank)

    def sleep(self):
        self.send_command(0x50)
        self.send_data(0xF7)
        self.send_command(0x02)
        self.send_command(0x07)
        self.send_data(0xA5)

        self.device.delay_ms(2000)
        self.device.module_exit()
