import json

import pytest

from guardians.model import GameModel
from guardians.storage import load_game, save_game


def test_save_and_load(tmp_path):
    path = tmp_path / "save.json"
    original = GameModel(seed=1234)
    original.perform_zone_action("river", 1)
    save_game(original, path)
    loaded = load_game(path)
    assert loaded.to_dict() == original.to_dict()


def test_missing_save_has_friendly_error(tmp_path):
    with pytest.raises(ValueError, match="找不到遊戲存檔"):
        load_game(tmp_path / "missing.json")


def test_malformed_json_has_friendly_error(tmp_path):
    path = tmp_path / "broken.json"
    path.write_text("not json", encoding="utf-8")
    with pytest.raises(ValueError, match="無法讀取存檔"):
        load_game(path)

