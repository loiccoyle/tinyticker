from typing import Dict

from ._base import TickerBase
from .crypto import TickerCrypto
from .stock import TickerStock

__all__ = ["TickerStock", "TickerCrypto"]


_SYMBOL_TYPES_TICKER: Dict[str, type[TickerBase]] = {
    "crypto": TickerCrypto,
    "stock": TickerStock,
}
SYMBOL_TYPES = list(_SYMBOL_TYPES_TICKER.keys())


def get_ticker_from_symbol_type(symbol_type: str) -> type[TickerBase]:
    """Get the `Ticker` class for a given symbol type."""
    return _SYMBOL_TYPES_TICKER[symbol_type]
