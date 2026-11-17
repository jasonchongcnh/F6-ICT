"""Load and validate data-driven event cards."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .config import EVENTS_PATH

ALLOWED_STATS = {
    "water", "food", "wood", "trust", "ecology", "community", "hope"
}


@dataclass(frozen=True)
class Choice:
    label: str
    description: str
    effects: dict[str, int]
    delayed: dict[str, Any] | None = None


@dataclass(frozen=True)
class Event:
    event_id: str
    title: str
    text: str
    choices: tuple[Choice, ...]


def _validate_effects(effects: object, context: str) -> dict[str, int]:
    if not isinstance(effects, dict):
        raise ValueError(f"{context}: effects must be an object")
    result: dict[str, int] = {}
    for key, value in effects.items():
        if key not in ALLOWED_STATS or not isinstance(value, int):
            raise ValueError(f"{context}: invalid effect {key!r}={value!r}")
        result[key] = value
    return result


def load_events(path: Path = EVENTS_PATH) -> list[Event]:
    """Return validated events or raise a clear configuration error."""
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Could not load event data: {exc}") from exc
    if not isinstance(raw, list) or len(raw) < 3:
        raise ValueError("Event data must contain at least three events")

    events: list[Event] = []
    seen: set[str] = set()
    for index, item in enumerate(raw):
        context = f"event {index}"
        if not isinstance(item, dict):
            raise ValueError(f"{context}: must be an object")
        event_id = item.get("id")
        if not isinstance(event_id, str) or not event_id or event_id in seen:
            raise ValueError(f"{context}: id must be unique and non-empty")
        seen.add(event_id)
        choices_raw = item.get("choices")
        if not isinstance(choices_raw, list) or not 2 <= len(choices_raw) <= 4:
            raise ValueError(f"{context}: needs two to four choices")
        choices: list[Choice] = []
        for choice_index, choice in enumerate(choices_raw):
            choice_context = f"{context}, choice {choice_index}"
            if not isinstance(choice, dict):
                raise ValueError(f"{choice_context}: must be an object")
            delayed = choice.get("delayed")
            if delayed is not None:
                if not isinstance(delayed, dict) or not isinstance(delayed.get("rounds"), int):
                    raise ValueError(f"{choice_context}: invalid delayed effect")
                delayed = {
                    "rounds": delayed["rounds"],
                    "message": str(delayed.get("message", "Earlier choices take effect.")),
                    "effects": _validate_effects(delayed.get("effects", {}), choice_context),
                }
            choices.append(
                Choice(
                    label=str(choice.get("label", "Choose")),
                    description=str(choice.get("description", "")),
                    effects=_validate_effects(choice.get("effects", {}), choice_context),
                    delayed=delayed,
                )
            )
        events.append(
            Event(
                event_id=event_id,
                title=str(item.get("title", "Island event")),
                text=str(item.get("text", "A decision is needed.")),
                choices=tuple(choices),
            )
        )
    return events

