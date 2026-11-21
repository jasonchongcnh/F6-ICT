"""獨立於 Pygame 渲染的固定種子遊戲模型。"""

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
        {"name": "適量伐木", "effects": {"wood": 12, "ecology": -4, "community": 2}},
        {"name": "種植原生樹木", "effects": {"wood": -5, "ecology": 10, "hope": 3}},
    ),
    "river": (
        {"name": "收集食水", "effects": {"water": 13, "ecology": -3}},
        {"name": "清理河流", "effects": {"water": -4, "ecology": 9, "community": 4}},
    ),
    "farm": (
        {"name": "收割農作物", "effects": {"food": 13, "ecology": -3}},
        {"name": "再生農耕", "effects": {"food": 5, "ecology": 6, "hope": 3}},
    ),
    "village": (
        {"name": "分享物資", "effects": {"food": -7, "wood": -3, "community": 9, "trust": 7, "hope": 5}},
        {"name": "社區工作坊", "effects": {"wood": -4, "community": 6, "trust": 4, "hope": 4}},
    ),
}


class GameModel:
    """管理遊戲規則、狀態轉換、隨機次序及結局。"""

    def __init__(self, seed: int | None = None, events: list[Event] | None = None) -> None:
        actual_seed = seed if seed is not None else random.SystemRandom().randrange(1, 1_000_000)
        self.events = events or load_events()
        self._by_id = {event.event_id: event for event in self.events}
        self.state = GameState(seed=actual_seed)
        self._prepare_deck()
        self._log(f"管家之旅開始。重玩種子：{actual_seed}。")

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
                raise ValueError(f"未知數值：{stat}")
            value = getattr(self.state, stat) + change
            setattr(self.state, stat, max(MIN_VALUE, min(MAX_VALUE, value)))

    def perform_zone_action(self, zone: str, action_index: int) -> str:
        if self.state.finished or self.current_event:
            raise ValueError("現在不能執行行動")
        if self.state.actions_left <= 0:
            raise ValueError("本回合已沒有剩餘行動")
        if zone not in ZONE_ACTIONS or action_index not in range(len(ZONE_ACTIONS[zone])):
            raise ValueError("未知的區域行動")
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
        self._log(f"事件：{self._by_id[event_id].title}")

    def choose_event(self, choice_index: int) -> str:
        event = self.current_event
        if event is None or choice_index not in range(len(event.choices)):
            raise ValueError("未知的事件選項")
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
            self._log(f"延後效果——{item.message}：{self.describe_effects(item.effects)}")
        # Every household consumes essentials; healthier ecology cushions water loss.
        upkeep = {"food": -4, "water": -4 if self.state.ecology >= 35 else -7}
        self.apply_effects(upkeep)
        self._log(f"第 {self.state.round_number} 回合：社區日常消耗 {self.describe_effects(upkeep)}")
        self._check_collapse()

    def _check_collapse(self) -> None:
        if min(self.state.ecology, self.state.community, self.state.hope) <= 0:
            self.state.finished = True
            self.state.ending = "neglect"
            self._log("由於疏忽，島上的共同生活已經崩潰。")

    def finish_game(self) -> str:
        s = self.state
        balance = max(s.ecology, s.community, s.hope) - min(s.ecology, s.community, s.hope)
        values = (s.ecology, s.community, s.hope)
        if min(values) >= 58 and balance <= 25 and min(s.food, s.water) >= 15:
            ending = "faithful"
        elif (
            s.trust >= 75
            and s.community >= 65
            and s.hope >= 60
            and s.ecology >= 45
            and min(s.food, s.water) >= 15
        ):
            ending = "solidarity"
        elif s.ecology >= 75 and s.community >= 45:
            ending = "restoration"
        elif (s.food + s.water + s.wood) >= 210 and (s.ecology < 40 or s.community < 40):
            ending = "profit"
        else:
            ending = "neglect"
        s.finished = True
        s.ending = ending
        self._log(f"最終結局：{ending}。")
        return ending

    @staticmethod
    def describe_effects(effects: dict[str, int]) -> str:
        if not effects:
            return "沒有即時變化"
        labels = {
            "water": "食水", "food": "食物", "wood": "木材", "trust": "信任",
            "ecology": "生態", "community": "社區", "hope": "希望",
        }
        return "、".join(f"{labels[key]} {value:+d}" for key, value in effects.items())

    def to_dict(self) -> dict[str, Any]:
        return {"version": 1, "state": asdict(self.state)}

    @classmethod
    def from_dict(cls, data: dict[str, Any], events: list[Event] | None = None) -> "GameModel":
        if not isinstance(data, dict) or data.get("version") != 1 or not isinstance(data.get("state"), dict):
            raise ValueError("不支援或已損壞的存檔")
        raw = dict(data["state"])
        missing = {field.name for field in GameState.__dataclass_fields__.values()} - raw.keys()
        if missing:
            raise ValueError(f"存檔缺少欄位：{', '.join(sorted(missing))}")
        raw["pending"] = [PendingEffect(**item) for item in raw["pending"]]
        model = cls(seed=int(raw["seed"]), events=events)
        model.state = GameState(**raw)
        unknown_events = set(model.state.event_deck) - model._by_id.keys()
        if unknown_events:
            raise ValueError("存檔引用了不存在的事件")
        for stat in STAT_NAMES:
            value = getattr(model.state, stat)
            if not isinstance(value, int) or not MIN_VALUE <= value <= MAX_VALUE:
                raise ValueError(f"存檔中的 {stat} 數值無效")
        return model

