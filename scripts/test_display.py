# from PIL import Image
# 
# DISPLAY_SIZE=(250, 122)
# 
# 
# newImage = Image.new("1", DISPLAY_SIZE, 255)
# newImage.save("monocolor.bmp")


import epd2in13
import time
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

def main():
    epd = epd2in13.EPD()
    epd.init(epd.lut_full_update)

    # For simplicity, the arguments are explicit numerical coordinates
    print(epd2in13.EPD_WIDTH)
    print(epd2in13.EPD_HEIGHT)
    image = Image.new('1', (epd2in13.EPD_WIDTH, epd2in13.EPD_HEIGHT), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(image)
    draw.rectangle((epd2in13.EPD_WIDTH/2-10, epd2in13.EPD_HEIGHT/2-10, epd2in13.EPD_WIDTH/2+10, epd2in13.EPD_HEIGHT/2+10), fill = 0)
    epd.set_frame_memory(image, 0, 0)
    epd.display_frame()
    
if __name__ == '__main__':
    main()
