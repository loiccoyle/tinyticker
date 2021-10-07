import logging

from .display import Display
from .ticker import Ticker

logger = logging.getLogger(__name__)

logger.addHandler(logging.NullHandler())