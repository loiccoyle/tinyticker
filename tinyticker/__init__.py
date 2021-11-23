# type: ignore
import logging

from .display import Display
from .ticker import Ticker

logger = logging.getLogger(__name__)

logger.addHandler(logging.NullHandler())

__version__ = "0.1.4"
