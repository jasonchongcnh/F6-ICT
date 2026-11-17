"""Run deterministic strategy simulations and export balance evidence."""

from __future__ import annotations

import argparse
import csv
import random
from collections import Counter
from pathlib import Path

from guardians.model import GameModel

STRATEGIES = ("extractive", "restorative", "community", "balanced", "random")


def choose_zone_action(strategy: str, rng: random.Random, turn: int) -> tuple[str, int]:
    if strategy == "extractive":
        return (("forest", 0), ("river", 0), ("farm", 0))[turn % 3]
    if strategy == "restorative":
        return (("forest", 1), ("river", 1), ("farm", 1))[turn % 3]
    if strategy == "community":
        return ("village", turn % 2)
    if strategy == "balanced":
        return (("farm", 1), ("village", 1), ("river", 1), ("forest", 0))[turn % 4]
    return rng.choice(tuple((zone, index) for zone in ("forest", "river", "farm", "village") for index in (0, 1)))


def choose_event(model: GameModel, strategy: str, rng: random.Random) -> int:
    assert model.current_event is not None
    choices = model.current_event.choices
    if strategy == "random":
        return rng.randrange(len(choices))

    def score(index: int) -> float:
        effects = choices[index].effects
        if strategy == "extractive":
            weights = {"food": 2, "water": 2, "wood": 2, "ecology": 0, "community": 0, "hope": 0, "trust": 0}
        elif strategy == "restorative":
            weights = {"ecology": 3, "water": 0.5, "hope": 0.5}
        elif strategy == "community":
            weights = {"community": 2.5, "hope": 2, "trust": 1.5}
        else:
            # Prioritise the lowest core value, while avoiding exhausted essentials.
            state = model.state
            lowest = min(("ecology", "community", "hope"), key=lambda key: getattr(state, key))
            weights = {"ecology": 1, "community": 1, "hope": 1, lowest: 3, "food": 0.4, "water": 0.4}
        return sum(change * weights.get(stat, 0) for stat, change in effects.items())

    return max(range(len(choices)), key=score)


def simulate(seed: int, strategy: str) -> dict[str, int | str]:
    rng = random.Random(seed * 1009 + STRATEGIES.index(strategy))
    model = GameModel(seed=seed)
    turn = 0
    while not model.state.finished:
        for _ in range(model.state.actions_left):
            zone, action = choose_zone_action(strategy, rng, turn)
            model.perform_zone_action(zone, action)
            turn += 1
            if model.state.finished or model.current_event:
                break
        if model.current_event:
            model.choose_event(choose_event(model, strategy, rng))
    state = model.state
    return {
        "seed": seed,
        "strategy": strategy,
        "ending": state.ending or "unknown",
        "ecology": state.ecology,
        "community": state.community,
        "hope": state.hope,
        "food": state.food,
        "water": state.water,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=500, help="total simulations")
    parser.add_argument("--csv", type=Path, help="optional raw results path")
    args = parser.parse_args()
    rows = [simulate(index + 1, STRATEGIES[index % len(STRATEGIES)]) for index in range(args.runs)]
    print(f"Balance simulations: {len(rows)}")
    for strategy in STRATEGIES:
        subset = [row for row in rows if row["strategy"] == strategy]
        endings = Counter(str(row["ending"]) for row in subset)
        print(f"{strategy:11s}: " + ", ".join(f"{name}={count}" for name, count in sorted(endings.items())))
    if args.csv:
        args.csv.parent.mkdir(parents=True, exist_ok=True)
        with args.csv.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

