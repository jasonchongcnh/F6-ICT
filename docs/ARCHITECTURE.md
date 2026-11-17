# System Architecture and API Notes

## Module diagram

```text
main.py
  └─ GameApp (guardians/app.py) ─ input, scene loop, feedback, rendering
       ├─ UI helpers (guardians/ui.py) ─ buttons, text wrapping, value bars
       ├─ GameModel (guardians/model.py) ─ rules and state transitions
       │    └─ events.py + data/events.json ─ validated event definitions
       └─ storage.py ─ atomic JSON save/load

tests/ ─ model, event, storage, and rendered-flow regression checks
tools/balance_simulation.py ─ headless strategy harness
```

## Data flow

1. Pygame sends keyboard/mouse events to `GameApp.handle_event`.
2. The active scene maps input to a model command such as `perform_zone_action` or `choose_event`.
3. `GameModel` validates the command, changes resources/values, queues delayed effects, appends history, and checks endings.
4. `GameApp` reads the resulting state and renders the map, dashboard, feedback, or event card.
5. `storage.py` serialises only model state; UI objects and live processes never enter the save file.

## Main APIs

- `GameModel(seed)`: starts a deterministic game and shuffles a 12-event deck.
- `perform_zone_action(zone, action_index)`: spends one action and opens an event after action two.
- `choose_event(choice_index)`: applies immediate/delayed effects and advances the round.
- `to_dict()` / `from_dict(data)`: versioned, validated save boundary.
- `load_events(path)`: validates IDs, choice counts, stats, and delayed data before play.
- `save_game(model, path)` / `load_game(path)`: atomic replacement and friendly error handling.

## Design separation

The simulation imports no Pygame code, so tests and hundreds of playthroughs run quickly. The UI cannot silently change rules. JSON holds event content, while Python holds validated behaviour. This reduces regression risk and allows balance tuning without rewriting scenes.

