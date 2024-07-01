import pytest
from PIL import Image

from tinyticker.config import TinytickerConfig
from tinyticker.display import Display
from tinyticker.waveshare_lib._base import EPDMonochrome
from tinyticker.waveshare_lib.models import MODELS, EPDData

from .utils import CONFIG_PATH, DATA_DIR, expected_fig

TEXT_PLOT_FILE = DATA_DIR / "text_plot.jpg"


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


def _check_fig_ax(display, fig, ax):
    assert (
        fig.get_size_inches() * fig.dpi
        == (
            display.epd.height,
            display.epd.width,
        )
    ).all()
    assert ax.margins() == (0, 0)
    assert ax.axison is False


@pytest.fixture
def display():
    return Display(EPDMock())


def test_from_tt_config():
    tt_config = TinytickerConfig.from_file(CONFIG_PATH)
    tt_config.epd_model = "mock"
    display = Display.from_tinyticker_config(tt_config)
    assert display.flip == tt_config.flip


def test_text(display):
    text = "Some text"
    fig, ax = display.text(text)
    _check_fig_ax(display, fig, ax)
    assert ax.texts[0]._text == text  # type: ignore
    assert expected_fig(fig, TEXT_PLOT_FILE)
