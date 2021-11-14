from dataclasses import dataclass
from types import ModuleType

from . import epd2in13_V2, epd2in13b_V3


@dataclass
class EPDModel:
    name: str
    module: ModuleType
    desc: str
    has_highlight: bool  # if the model has a colour channel for highlights i.e. red, yellow, ...


MODELS = [
    EPDModel(
        "EPD_v2",
        epd2in13_V2,
        "Black and White 2.13 inch V2",
        has_highlight=False,
    ),
    EPDModel(
        "EPDb_v3",
        epd2in13b_V3,
        "Black, White and Red 2.13 inch V3",
        has_highlight=True,
    ),
]
MODELS = {model.name: model for model in MODELS}
