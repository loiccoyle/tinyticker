import logging
from datetime import timezone
from pathlib import Path
from unittest import TestCase

import pandas as pd
from PIL import Image

from tinyticker import __version__, utils


class TestUtils(TestCase):
    def test_now(self):
        now = utils.now()
        assert isinstance(now, pd.Timestamp)
        assert now.tzinfo == timezone.utc

    def test_check_for_update(self):
        assert not utils.check_for_update(__version__)
        assert utils.check_for_update("0.0.1")

    def test_trim(self):
        trim_file = Path(__file__).parents[1] / "data" / "trim.jpg"
        assert trim_file.is_file()
        img = Image.open(trim_file)
        img_trim = utils.trim(img)
        assert img_trim.size == (200, 133)

    def test_dashboard_qrcode(self):
        qrcode = utils.dashboard_qrcode(200, 200)
        assert qrcode.size == (200, 200)

    def test_set_verbosity(self):
        logger = logging.getLogger("tinyticker_test")
        logger = utils.set_verbosity(logger, 1)
        assert logger.level == logging.INFO
        logger = utils.set_verbosity(logger, 2)
        assert logger.level == logging.DEBUG
