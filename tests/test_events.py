import json

import pytest

from guardians.events import load_events


def test_shipped_events_are_valid_and_meaningful():
    events = load_events()
    assert len(events) >= 8
    assert all(2 <= len(event.choices) <= 4 for event in events)
    assert any(choice.delayed for event in events for choice in event.choices)


def test_invalid_stat_is_rejected(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text(
        json.dumps([
            {"id": f"e{i}", "choices": [
                {"effects": {"money": 1}}, {"effects": {"hope": 1}}
            ]} for i in range(3)
        ]),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="無效效果"):
        load_events(path)

