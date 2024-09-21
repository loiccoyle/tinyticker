import json
from shutil import copy

from tinyticker import config

from .utils import DATA_DIR, CONFIG_PATH

CONFIG_MISSING_SEQUENCE = DATA_DIR / "config_missing_sequence_field.json"
CONFIG_INVALID = DATA_DIR / "config_invalid.json"


def test_tt_config_from_file():
    tt_config = config.TinytickerConfig.from_file(CONFIG_PATH)
    assert len(tt_config.tickers) == 4
    assert tt_config.epd_model == "EPDbc"
    assert tt_config.to_dict().keys() == config.TinytickerConfig().to_dict().keys()


def test_tt_config_missing_sequence_field():
    tt_config = config.TinytickerConfig.from_file(CONFIG_MISSING_SEQUENCE)
    assert tt_config.to_dict().keys() == config.TinytickerConfig().to_dict().keys()
    assert tt_config.sequence == config.SequenceConfig()


def test_tt_config_to_file(tmp_path):
    tt_config = config.TinytickerConfig()
    test_file = tmp_path / "out_config.json"
    tt_config.to_file(test_file)
    assert config.TinytickerConfig.from_file(test_file) == tt_config


def test_tt_config_to_json():
    tt_config = config.TinytickerConfig()
    config_json = tt_config.to_json()
    config_dict = json.loads(config_json)
    assert config_dict == tt_config.to_dict()


def test_load_config_safe():
    tt_config = config.load_config_safe(CONFIG_PATH)
    assert len(tt_config.tickers) == 4
    assert tt_config.epd_model == "EPDbc"
    assert tt_config.to_dict().keys() == config.TinytickerConfig().to_dict().keys()


def test_load_config_safe_missing_file(tmp_path):
    config_file = tmp_path / "missing_config.json"
    tt_config = config.load_config_safe(config_file)
    assert tt_config == config.TinytickerConfig()
    assert config_file.is_file()


def test_load_config_safe_invalid_file(tmp_path):
    config_file = tmp_path / "config_invalid.json"
    copy(CONFIG_INVALID, config_file)
    tt_config = config.load_config_safe(config_file)
    assert tt_config == config.TinytickerConfig()
