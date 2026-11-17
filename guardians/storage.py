"""Safe JSON save/load operations."""

from __future__ import annotations

import json
from pathlib import Path

from .config import DEFAULT_SAVE_PATH
from .model import GameModel


def save_game(model: GameModel, path: Path = DEFAULT_SAVE_PATH) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    try:
        temporary.write_text(json.dumps(model.to_dict(), indent=2), encoding="utf-8")
        temporary.replace(path)
    except OSError as exc:
        raise ValueError(f"Could not save game: {exc}") from exc


def load_game(path: Path = DEFAULT_SAVE_PATH) -> GameModel:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError("No saved game was found") from exc
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Could not read save: {exc}") from exc
    return GameModel.from_dict(data)

