# Test Plan and Feasibility

Date: 17 November 2026

## Automated checks

| Area | Check | Expected result |
|---|---|---|
| Event data | Validate unique IDs, 2–4 choices, legal stats, delayed effects | Shipped JSON loads; malformed stats fail clearly |
| Core loop | Two actions open an event; choice advances round | State transitions occur once and in order |
| Rules | Values clamp to 0–100; invalid commands fail | No invalid dashboard values or actions during events |
| Replay | Same seed creates same event deck | Exact event order is reproducible |
| Save/load | Round trip and malformed/missing files | State preserved; friendly errors returned |
| Endings | Automated full playthrough | One of five named endings reached within 12 rounds |
| UI flow | Menu → play → event → next round renders under dummy display | No display-dependent crash |
| Accessibility | Keyboard toggles contrast and sound | Both modes change without leaving the scene |
| Smoke | Compile all modules and render screenshot | Clean exit and valid 800×600 image |

Run: `.venv/bin/python -m pytest -q`

## Manual classroom tests still required

Real-user evidence cannot be manufactured. Two classmates should test keyboard and mouse paths, readability, decision clarity, save/load, and a complete ending. Record tester names/consent as required by school policy, date, device, seed, observations, and changes. Capture a genuine dated video showing the testers and game.

## Performance and feasibility

The app targets 60 FPS at 800×600. It uses primitive drawing, system fonts, tiny JSON data, and no network or external assets. The model is lightweight enough for hundreds of headless sessions. Main risks are missing Pygame on a school PC, audio-device availability, and students being unable to explain AI-assisted code. Mitigations: pinned requirements, silent audio fallback, offline assets, README, architecture notes, tests, and student code review/Q&A practice.

