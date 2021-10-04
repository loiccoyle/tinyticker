#!/usr/bin/python
# -*- coding:utf-8 -*-
import logging
import time

from PIL import Image, ImageDraw

from .waveshare_lib import CONFIG, EPD

logging.basicConfig(level=logging.DEBUG)

try:
    logging.info("epd2in13_V2 Demo")

    epd = EPD()
    logging.info("init and Clear")
    epd.init(epd.FULL_UPDATE)
    epd.Clear(0xFF)

    logging.info("1.Drawing on the image...")
    image = Image.new("1", (epd.height, epd.width), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(image)
    font = draw.getfont()
    logging.info(font)
    logging.info(font.__dir__())

    draw.rectangle(((0, 0), (50, 50)), outline=0)
    draw.rectangle(((55, 0), (100, 50)), fill=0)
    draw.line([(0, 0), (50, 50)], fill=0, width=1)
    draw.line([(0, 50), (50, 0)], fill=0, width=1)
    draw.chord((10, 60, 50, 100), 0, 360, fill=0)
    draw.ellipse((55, 60, 95, 100), outline=0)
    draw.pieslice(((55, 60), (95, 100)), 90, 180, outline=0)
    draw.pieslice(((55, 60), (95, 100)), 270, 360, fill=0)
    draw.polygon([(110, 0), (110, 50), (150, 25)], outline=0)
    draw.polygon([(190, 0), (190, 50), (150, 25)], fill=0)
    draw.text((120, 60), "e-Paper demo", font=font, fill=0)
    draw.text((110, 90), u"微雪电子", font=font, fill=0)
    epd.display(epd.getbuffer(image))
    time.sleep(2)

    # read bmp file
    # logging.info("2.read bmp file...")
    # image = Image.open(os.path.join(picdir, "2in13.bmp"))
    # epd.display(epd.getbuffer(image))
    # time.sleep(2)

    # read bmp file on window
    # logging.info("3.read bmp file on window...")
    # # epd.Clear(0xFF)
    # image1 = Image.new("1", (epd.height, epd.width), 255)  # 255: clear the frame
    # bmp = Image.open(os.path.join(picdir, "100x100.bmp"))
    # image1.paste(bmp, (2, 2))
    # epd.display(epd.getbuffer(image1))
    # time.sleep(2)

    # # partial update
    logging.info("4.show time...")
    time_image = Image.new("1", (epd.height, epd.width), 255)
    time_draw = ImageDraw.Draw(time_image)

    epd.init(epd.FULL_UPDATE)
    epd.displayPartBaseImage(epd.getbuffer(time_image))

    epd.init(epd.PART_UPDATE)
    num = 0
    while True:
        time_draw.rectangle((120, 80, 220, 105), fill=255)
        time_draw.text((120, 80), time.strftime("%H:%M:%S"), font=font, fill=0)
        epd.displayPartial(epd.getbuffer(time_image))
        num = num + 1
        if num == 10:
            break
    # epd.Clear(0xFF)
    logging.info("Clear...")
    epd.init(epd.FULL_UPDATE)
    epd.Clear(0xFF)

    logging.info("Goto Sleep...")
    epd.sleep()

except IOError as e:
    logging.info(e)

except KeyboardInterrupt:
    logging.info("ctrl + c:")
    CONFIG.module_exit()
    exit()
