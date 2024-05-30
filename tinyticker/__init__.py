import logging
from importlib.metadata import version

from .config import SequenceConfig, TickerConfig, TinytickerConfig
from .display import Display
from .sequence import Sequence
from .tickers import Ticker, TickerCrypto, TickerStock

logger = logging.getLogger(__name__)

logger.addHandler(logging.NullHandler())

__version__ = version("tinyticker")
__all__ = [
    "Display",
    "Sequence",
    "SequenceConfig",
    "Ticker",
    "TickerConfig",
    "TickerCrypto",
    "TickerStock",
    "TinytickerConfig",
]
