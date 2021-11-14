from dataclasses import dataclass
from typing import Callable

from . import epd2in13_V2, epd2in13b_V3


@dataclass
class EPDModel:
    name: str
    class_: Callable
    desc: str
    has_highlight: bool  # if the model has a colour channel for highlights i.e. red, yellow, ...
    width: int
    height: int


MODELS = [
    EPDModel(
        name="EPD_v2",
        class_=epd2in13_V2.EPD,
        desc="Black and White 2.13 inch V2",
        has_highlight=False,
        width=epd2in13_V2.EPD_WIDTH,
        height=epd2in13_V2.EPD_HEIGHT,
    ),
    EPDModel(
        name="EPDb_v3",
        class_=epd2in13b_V3.EPD,
        desc="Black, White and Red 2.13 inch V3",
        has_highlight=True,
        width=epd2in13b_V3.EPD_WIDTH,
        height=epd2in13b_V3.EPD_HEIGHT,
    ),
]
MODELS = {model.name: model for model in MODELS}
