# Project Proposal — Guardians of Creation

Date created: 17 November 2026

## Design intent

The player is a newly appointed steward of Haven Island. In each of 12 rounds they receive two actions and choose where to serve: forest, river, farm, or village. Actions supply immediate needs but alter connected systems. Random dilemmas add sacrifice, justice, solidarity, and delayed consequences. A faithful ending requires balance rather than maximising one score.

Target audience: students aged 15–18 who can read short English instructions and use a keyboard or mouse.

## Quantifiable goals

- 800×600 display at a stable target of 60 FPS.
- Four interactive map zones and visible player movement.
- Three interacting layers: resources, values, and event consequences.
- At least eight events, each with two or three meaningful choices.
- Twelve rounds, two actions per round, delayed effects, deterministic seeded replay.
- At least three endings; the final build contains five.
- Save/load with validation and graceful error handling.
- Keyboard and mouse operation plus high contrast and sound toggles.
- Automated unit tests and at least 500 simulated balance runs.

## Core loop

Review dashboard → move to a zone → choose an action → observe resource/value feedback → resolve an event → apply delayed consequences → continue to the next round → receive a balanced ending.

## Theme interpretation

Stewardship is the actual optimisation problem. Harvesting and profit can meet urgent needs, but excessive extraction damages ecology and future productivity. Sharing costs food or wood but strengthens community and hope. Restoration consumes scarce actions now and creates delayed benefits. The good ending therefore rewards prudence, solidarity, justice, and care for creation.

## Scope and feasibility

The game uses only Python, Pygame CE, JSON, and Python’s standard library. Art and sound are generated in code, avoiding licensing and offline-runtime risks. Data-driven events and a separated simulation model allow systematic testing without opening a window.

