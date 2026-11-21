import pytest

from guardians.config import MAX_ROUNDS
from guardians.model import GameModel, ZONE_ACTIONS


def test_same_seed_creates_same_event_order():
    first = GameModel(seed=42)
    second = GameModel(seed=42)
    assert first.state.event_deck == second.state.event_deck


def test_zone_actions_consume_turn_and_open_event():
    model = GameModel(seed=1)
    model.perform_zone_action("forest", 0)
    assert model.state.actions_left == 1
    model.perform_zone_action("river", 1)
    assert model.state.actions_left == 0
    assert model.current_event is not None


def test_cannot_act_during_event():
    model = GameModel(seed=1)
    model.perform_zone_action("forest", 0)
    model.perform_zone_action("river", 0)
    with pytest.raises(ValueError, match="不能"):
        model.perform_zone_action("farm", 0)


def test_choice_advances_round_and_applies_upkeep():
    model = GameModel(seed=7)
    model.perform_zone_action("farm", 1)
    model.perform_zone_action("village", 1)
    food_before = model.state.food
    model.choose_event(0)
    assert model.state.round_number == 2
    assert model.state.actions_left == 2
    assert model.state.food <= min(100, food_before + 30)


def test_effects_are_clamped():
    model = GameModel(seed=2)
    model.apply_effects({"hope": 200, "water": -200})
    assert model.state.hope == 100
    assert model.state.water == 0


def test_all_zone_actions_have_tradeoffs_or_shared_benefits():
    for actions in ZONE_ACTIONS.values():
        for action in actions:
            assert len(action["effects"]) >= 2


def test_full_game_reaches_a_named_ending():
    model = GameModel(seed=99)
    while not model.state.finished:
        model.perform_zone_action("farm", 1)
        if not model.state.finished:
            model.perform_zone_action("village", 1)
        if model.current_event:
            model.choose_event(0)
    assert model.state.round_number <= MAX_ROUNDS + 1
    assert model.state.ending in {"faithful", "solidarity", "restoration", "profit", "neglect"}


def test_serialization_round_trip_preserves_state():
    model = GameModel(seed=321)
    model.perform_zone_action("forest", 1)
    restored = GameModel.from_dict(model.to_dict())
    assert restored.to_dict() == model.to_dict()


def test_corrupt_save_is_rejected():
    with pytest.raises(ValueError, match="不支援"):
        GameModel.from_dict({"version": 99})

