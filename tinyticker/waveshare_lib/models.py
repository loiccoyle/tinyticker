from dataclasses import dataclass
from typing import Type, Union

from . import (
    epd2in7,
    epd2in7_V2,
    epd2in13,
    epd2in13_V2,
    epd2in13_V3,
    epd2in13_V4,
    epd2in13b_V3,
    epd2in13b_V4,
    epd2in13bc,
    epd7in5b_V2,
)
from ._base import EPDHighlight, EPDMonochrome, EPDGrayscale

EPDModel = Union[EPDMonochrome, EPDHighlight, EPDGrayscale]


@dataclass
class EPDData:
    name: str
    EPD: Union[Type[EPDMonochrome], Type[EPDHighlight], Type[EPDGrayscale]]
    desc: str


MODELS = [
    EPDData(
        name="EPD",
        EPD=epd2in13.EPD,
        desc="Black and White 2.13 inch",
    ),
    EPDData(
        name="EPD_v2",
        EPD=epd2in13_V2.EPD,
        desc="Black and White 2.13 inch V2",
    ),
    EPDData(
        name="EPD_v3",
        EPD=epd2in13_V3.EPD,
        desc="Black and White 2.13 inch V3",
    ),
    EPDData(
        name="EPD_v4",
        EPD=epd2in13_V4.EPD,
        desc="Black and White 2.13 inch V4",
    ),
    EPDData(
        name="EPDb_v3",
        EPD=epd2in13b_V3.EPD,
        desc="Black, White and Red 2.13 inch V3",
    ),
    EPDData(
        name="EPDb_v4",
        EPD=epd2in13b_V4.EPD,
        desc="Black, White and Red 2.13 inch V4",
    ),
    EPDData(
        name="EPDbc",
        EPD=epd2in13bc.EPD,
        desc="Black, White and Yellow 2.13 inch",
    ),
    EPDData(
        name="EPD_2in7",
        EPD=epd2in7.EPD,
        desc="Black and White 2.7 inch",
    ),
    EPDData(
        name="EPD_2in7_v2",
        EPD=epd2in7_V2.EPD,
        desc="Black and White 2.7 inch V2",
    ),
    EPDData(
        name="EPD_7in5b_v2",
        EPD=epd7in5b_V2.EPD,
        desc="Black, White and Red 7.5 inch V2",
    ),
]
MODELS = {model.name: model for model in MODELS}
