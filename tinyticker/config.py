import dataclasses
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Union

LOGGER = logging.getLogger(__name__)

# remove hollow types because white on white doesn't show
PLOT_TYPES = ["candlestick", "line", "ohlc"]


@dataclass
class TickerConfig:
    symbol_type: str = "stock"
    symbol: str = "SPY"
    interval: str = "1d"
    lookback: Optional[int] = None
    wait_time: Optional[int] = None
    plot_type: str = "candlestick"
    mav: Optional[int] = None


@dataclass
class TinytickerConfig:
    tickers: List[TickerConfig] = [TickerConfig()]
    epd_model: str = "EPD_v3"
    api_key: Optional[str] = None
    flip: bool = False

    @classmethod
    def from_file(cls, file: Path) -> "TinytickerConfig":
        with file.open("r") as fp:
            data = json.load(fp)
        return cls.from_json(data)

    def to_file(self, file: Path) -> None:
        with file.open("w") as fp:
            json.dump(self.to_dict(), fp)

    @classmethod
    def from_json(cls, json_: Union[str, bytes, bytearray]) -> "TinytickerConfig":
        data = json.loads(json_)
        data["tickers"] = [
            TickerConfig(**ticker_data) for ticker_data in data["tickers"]
        ]
        return cls(**data)

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)
