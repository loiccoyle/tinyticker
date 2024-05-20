import json
from pathlib import Path
from shutil import copy, rmtree
from unittest import TestCase

from tinyticker import config


class TestConfig(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_dir = Path("test_config")
        cls.data_dir = Path(__file__).parents[1] / "data"
        if not cls.test_dir.is_dir():
            cls.test_dir.mkdir()

    def test_tt_config_from_file(self):
        config_file = self.data_dir / "config.json"
        tt_config = config.TinytickerConfig.from_file(config_file)
        assert len(tt_config.tickers) == 4
        assert tt_config.epd_model == "EPDbc"
        assert tt_config.to_dict().keys() == config.TinytickerConfig().to_dict().keys()

    def test_tt_config_missing_sequence_field(self):
        config_file = self.data_dir / "config_missing_sequence_field.json"
        tt_config = config.TinytickerConfig.from_file(config_file)
        assert tt_config.to_dict().keys() == config.TinytickerConfig().to_dict().keys()
        assert tt_config.sequence == config.SequenceConfig()

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

    def test_load_config_safe(self):
        config_file = self.data_dir / "config.json"
        tt_config = config.load_config_safe(config_file)
        assert len(tt_config.tickers) == 4
        assert tt_config.epd_model == "EPDbc"
        assert tt_config.to_dict().keys() == config.TinytickerConfig().to_dict().keys()

    def test_load_config_safe_missing_file(self):
        config_file = self.test_dir / "missing_config.json"
        tt_config = config.load_config_safe(config_file)
        assert tt_config == config.TinytickerConfig()
        assert config_file.is_file()

    def test_load_config_safe_invalid_file(self):
        copy(
            self.data_dir / "config_invalid.json", self.test_dir / "config_invalid.json"
        )
        config_file = self.test_dir / "config_invalid.json"
        tt_config = config.load_config_safe(config_file)
        assert tt_config == config.TinytickerConfig()

    @classmethod
    def tearDownClass(cls):
        if cls.test_dir.is_dir():
            rmtree(cls.test_dir)
