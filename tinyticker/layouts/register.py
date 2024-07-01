import dataclasses as dc
from typing import Callable, Optional, Tuple

from PIL import Image

from ..tickers._base import TickerBase, TickerResponse

LayoutFunc = Callable[[Tuple[int, int], TickerBase, TickerResponse], Image.Image]
LAYOUTS = {}


@dc.dataclass
class LayoutData:
    func: LayoutFunc
    name: str
    desc: Optional[str]


def register(func: LayoutFunc) -> LayoutFunc:
    """Register a layout function.

    Args:
        func: the layout function to register.

    Returns:
        The layout function.
    """
    layout = LayoutData(
        func=func, name=func.__name__.replace("_", " "), desc=func.__doc__
    )
    LAYOUTS[layout.name] = layout
    return func
