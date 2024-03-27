import json
from pathlib import Path
from shutil import rmtree
from unittest import TestCase

from tinyticker import config


class TestConfig(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_dir = Path("test_config")
        if not cls.test_dir.is_dir():
            cls.test_dir.mkdir()

    def test_tt_config_from_file(self):
        config_file = Path(__file__).parents[1] / "data" / "config.json"
        tt_config = config.TinytickerConfig.from_file(config_file)
        assert len(tt_config.tickers) == 4
        assert tt_config.epd_model == "EPDbc"

    def test_tt_config_to_file(self):
        tt_config = config.TinytickerConfig()
        test_file = self.test_dir / "out_config.json"
        tt_config.to_file(test_file)
        assert config.TinytickerConfig.from_file(test_file) == tt_config

    def test_tt_config_to_json(self):
        tt_config = config.TinytickerConfig()
        config_json = tt_config.to_json()
        config_dict = json.loads(config_json)
        assert config_dict == tt_config.to_dict()

    @classmethod
    def tearDownClass(cls):
        if cls.test_dir.is_dir():
            rmtree(cls.test_dir)
