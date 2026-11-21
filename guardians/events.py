"""載入並驗證資料驅動的事件卡。"""

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
        raise ValueError(f"{context}：效果必須是物件")
    result: dict[str, int] = {}
    for key, value in effects.items():
        if key not in ALLOWED_STATS or not isinstance(value, int):
            raise ValueError(f"{context}：無效效果 {key!r}={value!r}")
        result[key] = value
    return result


def load_events(path: Path = EVENTS_PATH) -> list[Event]:
    """傳回已驗證事件，或提出清晰的設定錯誤。"""
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"無法載入事件資料：{exc}") from exc
    if not isinstance(raw, list) or len(raw) < 3:
        raise ValueError("事件資料必須包含至少三個事件")

    events: list[Event] = []
    seen: set[str] = set()
    for index, item in enumerate(raw):
        context = f"事件 {index}"
        if not isinstance(item, dict):
            raise ValueError(f"{context}：必須是物件")
        event_id = item.get("id")
        if not isinstance(event_id, str) or not event_id or event_id in seen:
            raise ValueError(f"{context}：識別碼必須唯一且不可留空")
        seen.add(event_id)
        choices_raw = item.get("choices")
        if not isinstance(choices_raw, list) or not 2 <= len(choices_raw) <= 4:
            raise ValueError(f"{context}：需要兩至四個選項")
        choices: list[Choice] = []
        for choice_index, choice in enumerate(choices_raw):
            choice_context = f"{context}，選項 {choice_index}"
            if not isinstance(choice, dict):
                raise ValueError(f"{choice_context}：必須是物件")
            delayed = choice.get("delayed")
            if delayed is not None:
                if not isinstance(delayed, dict) or not isinstance(delayed.get("rounds"), int):
                    raise ValueError(f"{choice_context}：無效的延後效果")
                delayed = {
                    "rounds": delayed["rounds"],
                    "message": str(delayed.get("message", "先前的選擇開始產生效果。")),
                    "effects": _validate_effects(delayed.get("effects", {}), choice_context),
                }
            choices.append(
                Choice(
                    label=str(choice.get("label", "選擇")),
                    description=str(choice.get("description", "")),
                    effects=_validate_effects(choice.get("effects", {}), choice_context),
                    delayed=delayed,
                )
            )
        events.append(
            Event(
                event_id=event_id,
                title=str(item.get("title", "島嶼事件")),
                text=str(item.get("text", "現在需要作出決定。")),
                choices=tuple(choices),
            )
        )
    return events

