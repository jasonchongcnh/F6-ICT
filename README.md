# Guardians of Creation

An offline Pygame management game for the Form 6 theme **“The Good Steward: Guardians of Creation.”** The player crosses a small island and spends two actions per round caring for its forest, river, farm, and community. Choices trade short-term resources against Ecology, Community Well-being, and Hope. The island reaches one of several endings after 12 rounds—or earlier if a vital value collapses.

## Run

Python 3.11+ is recommended.

```bash
python -m pip install -r requirements.txt
python main.py
```

The game is self-contained and works offline after installation. All visuals and sound effects are generated in code; there are no third-party media assets.

## Controls

- `WASD` / arrow keys: move between island zones
- `Enter` / `Space`: interact with the current zone or activate a focused button
- Mouse: select buttons and event choices
- `Esc`: pause or return
- `F5`: save; `F9`: load
- `M`: toggle sound; `C`: high-contrast mode

The main menu includes instructions, new game, load, accessibility, and exit. During play, the pause menu provides save, resume, restart, and menu actions.

## Development checks

```bash
pytest -q
python tools/balance_simulation.py --runs 500
```

See `docs/` and `evidence/` for architecture, process records, tests, and submission guidance.

