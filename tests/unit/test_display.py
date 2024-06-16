from pathlib import Path
from unittest import TestCase

import pandas as pd
from PIL import Image

from tinyticker.config import TinytickerConfig
from tinyticker.display import Display
from tinyticker.waveshare_lib._base import EPDMonochrome
from tinyticker.waveshare_lib.models import MODELS, EPDData

from .utils import expected_fig


class EPDMock(EPDMonochrome):
    width = 122
    height = 250

    def __init__(self) -> None:
        self.is_init = False

    def init(self) -> None:
        self.is_init = True

    def getbuffer(self, image: Image.Image) -> bytearray:
        return bytearray()

    def display(self, image: bytearray) -> None:
        pass

    def clear(self) -> None:
        pass

    def sleep(self) -> None:
        pass


MODELS["mock"] = EPDData(
    name="mock",
    EPD=EPDMock,
    desc="A Mock display for testing",
)


class TestDisplay(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.display = Display(EPDMock())
        cls.data_dir = Path(__file__).parents[1] / "data"
        cls.config_path = cls.data_dir / "config.json"
        cls.historical: pd.DataFrame = pd.read_pickle(
            cls.data_dir / "crypto_historical.pkl"
        )
        cls.text_plot_file = cls.data_dir / "text_plot.jpg"

    def test_from_tt_config(self):
        tt_config = TinytickerConfig.from_file(self.config_path)
        tt_config.epd_model = "mock"
        display = Display.from_tinyticker_config(tt_config)
        assert display.flip == tt_config.flip

    def _check_fig_ax(self, fig, ax):
        assert (
            fig.get_size_inches() * fig.dpi
            == (
                self.display.epd.height,
                self.display.epd.width,
            )
        ).all()
        assert ax.margins() == (0, 0)
        assert ax.axison is False

    def test_text(self):
        text = "Some text"
        fig, ax = self.display.text(text)
        self._check_fig_ax(fig, ax)
        assert ax.texts[0]._text == text  # type: ignore
        assert expected_fig(fig, self.text_plot_file)
