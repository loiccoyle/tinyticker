from dataclasses import dataclass
from typing import Type, Union

from . import (
    epd2in13,
    epd2in13_V2,
    epd2in13_V3,
    epd2in13_V4,
    epd2in13b_V3,
    epd2in13b_V4,
    epd2in13bc,
)
from ._base import EPDMonochrome, EPDHighlight


@dataclass
class EPDModel:
    name: str
    class_: Union[Type[EPDMonochrome], Type[EPDHighlight]]
    desc: str


MODELS = [
    EPDModel(
        name="EPD",
        class_=epd2in13.EPD,
        desc="Black and White 2.13 inch",
    ),
    EPDModel(
        name="EPD_v2",
        class_=epd2in13_V2.EPD,
        desc="Black and White 2.13 inch V2",
    ),
    EPDModel(
        name="EPD_v3",
        class_=epd2in13_V3.EPD,
        desc="Black and White 2.13 inch V3",
    ),
    EPDModel(
        name="EPD_v4",
        class_=epd2in13_V4.EPD,
        desc="Black and White 2.13 inch V4",
    ),
    EPDModel(
        name="EPDb_v3",
        class_=epd2in13b_V3.EPD,
        desc="Black, White and Red 2.13 inch V3",
    ),
    EPDModel(
        name="EPDb_v4",
        class_=epd2in13b_V4.EPD,
        desc="Black, White and Red 2.13 inch V4",
    ),
    EPDModel(
        name="EPDbc",
        class_=epd2in13bc.EPD,
        desc="Black, White and Yellow 2.13 inch",
    ),
]
MODELS = {model.name: model for model in MODELS}
