import dataclasses as dc
import json
import logging
from pathlib import Path
from typing import List, Optional, Union

LOGGER = logging.getLogger(__name__)

# remove hollow types because white on white doesn't show
PLOT_TYPES = ["candle", "line", "ohlc"]


@dc.dataclass
class TickerConfig:
    symbol_type: str = "stock"
    symbol: str = "SPY"
    interval: str = "1d"
    lookback: Optional[int] = None
    wait_time: Optional[int] = None
    plot_type: str = "candle"
    mav: Optional[int] = None
    volume: bool = False
    avg_buy_price: Optional[float] = None


@dc.dataclass
class SequenceConfig:
    skip_outdated: bool = True
    skip_empty: bool = True


@dc.dataclass
class TinytickerConfig:
    tickers: List[TickerConfig] = dc.field(default_factory=lambda: [TickerConfig()])
    sequence: SequenceConfig = dc.field(default_factory=lambda: SequenceConfig())
    epd_model: str = "EPD_v4"
    api_key: Optional[str] = None
    flip: bool = False

    @classmethod
    def from_file(cls, file: Path) -> "TinytickerConfig":
        with file.open("r") as fp:
            return cls.from_json(fp.read())

    def to_file(self, file: Path) -> None:
        with file.open("w") as fp:
            json.dump(self.to_dict(), fp, indent=2)

    @classmethod
    def from_json(cls, json_: Union[str, bytes, bytearray]) -> "TinytickerConfig":
        data = json.loads(json_)
        data["tickers"] = [
            TickerConfig(**ticker_data) for ticker_data in data["tickers"]
        ]
        data["sequence"] = SequenceConfig(
            **data.get("sequence", dc.asdict(SequenceConfig()))
        )
        return cls(**data)

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    def to_dict(self) -> dict:
        return dc.asdict(self)
