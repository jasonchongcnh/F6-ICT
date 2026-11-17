"""Deterministic game simulation, independent of Pygame rendering."""

from __future__ import annotations

import random
from dataclasses import asdict, dataclass, field
from typing import Any

from .config import ACTIONS_PER_ROUND, MAX_ROUNDS, MAX_VALUE, MIN_VALUE
from .events import Event, load_events

STAT_NAMES = ("water", "food", "wood", "trust", "ecology", "community", "hope")


@dataclass
class PendingEffect:
    due_round: int
    message: str
    effects: dict[str, int]


@dataclass
class GameState:
    seed: int
    round_number: int = 1
    actions_left: int = ACTIONS_PER_ROUND
    water: int = 55
    food: int = 55
    wood: int = 35
    trust: int = 50
    ecology: int = 60
    community: int = 55
    hope: int = 55
    current_zone: str = "village"
    event_deck: list[str] = field(default_factory=list)
    event_index: int = 0
    current_event_id: str | None = None
    pending: list[PendingEffect] = field(default_factory=list)
    history: list[str] = field(default_factory=list)
    finished: bool = False
    ending: str | None = None


ZONE_ACTIONS: dict[str, tuple[dict[str, Any], ...]] = {
    "forest": (
        {"name": "Careful harvest", "effects": {"wood": 12, "ecology": -4, "community": 2}},
        {"name": "Plant native trees", "effects": {"wood": -5, "ecology": 10, "hope": 3}},
    ),
    "river": (
        {"name": "Collect water", "effects": {"water": 13, "ecology": -3}},
        {"name": "Clean the river", "effects": {"water": -4, "ecology": 9, "community": 4}},
    ),
    "farm": (
        {"name": "Gather harvest", "effects": {"food": 13, "ecology": -3}},
        {"name": "Regenerative farming", "effects": {"food": 5, "ecology": 6, "hope": 3}},
    ),
    "village": (
        {"name": "Share supplies", "effects": {"food": -7, "wood": -3, "community": 9, "trust": 7, "hope": 5}},
        {"name": "Community workshop", "effects": {"wood": -4, "community": 6, "trust": 4, "hope": 4}},
    ),
}


class GameModel:
    """Owns game rules, state transitions, random order, and endings."""

    def __init__(self, seed: int | None = None, events: list[Event] | None = None) -> None:
        actual_seed = seed if seed is not None else random.SystemRandom().randrange(1, 1_000_000)
        self.events = events or load_events()
        self._by_id = {event.event_id: event for event in self.events}
        self.state = GameState(seed=actual_seed)
        self._prepare_deck()
        self._log(f"Stewardship begins. Replay seed: {actual_seed}.")

    def _prepare_deck(self) -> None:
        rng = random.Random(self.state.seed)
        deck = [event.event_id for event in self.events]
        while len(deck) < MAX_ROUNDS:
            deck.extend(event.event_id for event in self.events)
        rng.shuffle(deck)
        self.state.event_deck = deck[:MAX_ROUNDS]

    @property
    def current_event(self) -> Event | None:
        event_id = self.state.current_event_id
        return self._by_id.get(event_id) if event_id else None

    def _log(self, message: str) -> None:
        self.state.history.append(message)
        self.state.history = self.state.history[-30:]

    def apply_effects(self, effects: dict[str, int]) -> None:
        for stat, change in effects.items():
            if stat not in STAT_NAMES:
                raise ValueError(f"Unknown stat: {stat}")
            value = getattr(self.state, stat) + change
            setattr(self.state, stat, max(MIN_VALUE, min(MAX_VALUE, value)))

    def perform_zone_action(self, zone: str, action_index: int) -> str:
        if self.state.finished or self.current_event:
            raise ValueError("An action cannot be taken now")
        if self.state.actions_left <= 0:
            raise ValueError("No actions remain this round")
        if zone not in ZONE_ACTIONS or action_index not in range(len(ZONE_ACTIONS[zone])):
            raise ValueError("Unknown zone action")
        action = ZONE_ACTIONS[zone][action_index]
        self.apply_effects(action["effects"])
        self.state.actions_left -= 1
        self.state.current_zone = zone
        summary = self.describe_effects(action["effects"])
        message = f"{action['name']}: {summary}"
        self._log(message)
        self._check_collapse()
        if not self.state.finished and self.state.actions_left == 0:
            self._open_next_event()
        return message

    def _open_next_event(self) -> None:
        event_id = self.state.event_deck[self.state.event_index]
        self.state.event_index += 1
        self.state.current_event_id = event_id
        self._log(f"Event: {self._by_id[event_id].title}")

    def choose_event(self, choice_index: int) -> str:
        event = self.current_event
        if event is None or choice_index not in range(len(event.choices)):
            raise ValueError("Unknown event choice")
        choice = event.choices[choice_index]
        self.apply_effects(choice.effects)
        if choice.delayed:
            self.state.pending.append(
                PendingEffect(
                    due_round=self.state.round_number + choice.delayed["rounds"],
                    message=choice.delayed["message"],
                    effects=dict(choice.delayed["effects"]),
                )
            )
        message = f"{choice.label}: {self.describe_effects(choice.effects)}"
        self._log(message)
        self.state.current_event_id = None
        self._check_collapse()
        if not self.state.finished:
            self._advance_round()
        return message

    def _advance_round(self) -> None:
        self.state.round_number += 1
        if self.state.round_number > MAX_ROUNDS:
            self.finish_game()
            return
        self.state.actions_left = ACTIONS_PER_ROUND
        due = [item for item in self.state.pending if item.due_round <= self.state.round_number]
        self.state.pending = [item for item in self.state.pending if item not in due]
        for item in due:
            self.apply_effects(item.effects)
            self._log(f"Delayed effect — {item.message}: {self.describe_effects(item.effects)}")
        # Every household consumes essentials; healthier ecology cushions water loss.
        upkeep = {"food": -4, "water": -4 if self.state.ecology >= 35 else -7}
        self.apply_effects(upkeep)
        self._log(f"Round {self.state.round_number}: community needs {self.describe_effects(upkeep)}")
        self._check_collapse()

    def _check_collapse(self) -> None:
        if min(self.state.ecology, self.state.community, self.state.hope) <= 0:
            self.state.finished = True
            self.state.ending = "neglect"
            self._log("The island's shared life has collapsed through neglect.")

    def finish_game(self) -> str:
        s = self.state
        balance = max(s.ecology, s.community, s.hope) - min(s.ecology, s.community, s.hope)
        values = (s.ecology, s.community, s.hope)
        if min(values) >= 58 and balance <= 25 and min(s.food, s.water) >= 15:
            ending = "faithful"
        elif s.trust >= 75 and s.community >= 65 and s.hope >= 60:
            ending = "solidarity"
        elif s.ecology >= 75 and s.community >= 45:
            ending = "restoration"
        elif (s.food + s.water + s.wood) >= 210 and (s.ecology < 40 or s.community < 40):
            ending = "profit"
        else:
            ending = "neglect"
        s.finished = True
        s.ending = ending
        self._log(f"Final ending: {ending}.")
        return ending

    @staticmethod
    def describe_effects(effects: dict[str, int]) -> str:
        if not effects:
            return "no immediate change"
        return ", ".join(f"{key.title()} {value:+d}" for key, value in effects.items())

    def to_dict(self) -> dict[str, Any]:
        return {"version": 1, "state": asdict(self.state)}

    @classmethod
    def from_dict(cls, data: dict[str, Any], events: list[Event] | None = None) -> "GameModel":
        if not isinstance(data, dict) or data.get("version") != 1 or not isinstance(data.get("state"), dict):
            raise ValueError("Unsupported or damaged save file")
        raw = dict(data["state"])
        missing = {field.name for field in GameState.__dataclass_fields__.values()} - raw.keys()
        if missing:
            raise ValueError(f"Save file is missing: {', '.join(sorted(missing))}")
        raw["pending"] = [PendingEffect(**item) for item in raw["pending"]]
        model = cls(seed=int(raw["seed"]), events=events)
        model.state = GameState(**raw)
        unknown_events = set(model.state.event_deck) - model._by_id.keys()
        if unknown_events:
            raise ValueError("Save file refers to unavailable events")
        for stat in STAT_NAMES:
            value = getattr(model.state, stat)
            if not isinstance(value, int) or not MIN_VALUE <= value <= MAX_VALUE:
                raise ValueError(f"Save file has invalid {stat}")
        return model

