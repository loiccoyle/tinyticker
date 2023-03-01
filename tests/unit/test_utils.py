import datetime
from pathlib import Path
from unittest import TestCase

from PIL import Image

from tinyticker import __version__, utils


class TestUtils(TestCase):
    def test_now(self):
        now = utils.now()
        assert isinstance(now, datetime.datetime)
        assert now.tzinfo == datetime.timezone.utc

    def test_check_for_update(self):
        assert not utils.check_for_update(__version__)
        assert utils.check_for_update("0.0.1")

    def test_trim(self):
        trim_file = Path(__file__).parents[1] / "data" / "trim.jpg"
        assert trim_file.is_file()
        img = Image.open(trim_file)
        img_trim = utils.trim(img)
        assert img_trim.size == (200, 133)
