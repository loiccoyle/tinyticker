from typing import Dict

from ..config import TickerConfig, TinytickerConfig
from ._base import TickerBase, TickerResponse
from .crypto import TickerCrypto
from .stock import TickerStock

__all__ = ["TickerStock", "TickerCrypto", "Ticker", "TickerResponse", "TickerBase"]


_SYMBOL_TYPES_TICKER: Dict[str, type[TickerBase]] = {
    "crypto": TickerCrypto,
    "stock": TickerStock,
}
SYMBOL_TYPES = list(_SYMBOL_TYPES_TICKER.keys())


class Ticker:
    """Factory class to create a `Ticker` instance from a `TinytickerConfig` and a `TickerConfig`."""

    @staticmethod
    def _get_ticker_class_from_symbol_type(symbol_type: str) -> type[TickerBase]:
        """Get the `Ticker` class for a given symbol type."""
        return _SYMBOL_TYPES_TICKER[symbol_type]

    def __new__(
        cls, tt_config: TinytickerConfig, ticker_config: TickerConfig
    ) -> TickerBase:
        """Create a Ticker instance from a `TinytickerConfig` and `TickerConfig`."""
        ticker_class = cls._get_ticker_class_from_symbol_type(ticker_config.symbol_type)
        return ticker_class.from_config(tt_config, ticker_config)
