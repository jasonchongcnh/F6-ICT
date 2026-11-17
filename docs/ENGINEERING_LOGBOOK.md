# Engineering Logbook — Guardians of Creation

This is the editable source for the final Google Docs/PDF logbook. Replace blanks only with truthful student evidence. AI assistance is declared in `AI_USE_LOG.md`.

## Project identity

- Assigned theme: The Good Steward — Guardians of Creation
- Members: _Student 1_ and _Student 2_
- Development period: 3–24 November 2026
- Final deadline: 24 November 2026, 23:59

## 3 November checkpoint — student completion required

The supplied conversation contains no verifiable record from 3 November. Attach the genuine group-formation record, proposal draft, theme confirmation, research plan, and Meeting 1 notes if they exist. Do not recreate or backdate evidence.

## 10 November checkpoint — student completion required

The supplied conversation contains no dated prototype recording from 10 November. Attach the original 30–90 second unedited video and matching code snapshot/commit if they exist. Record the filename, capture date, speakers, demonstrated features, and teacher feedback. Do not label a later recording as 10 November evidence.

## 17 November — beta engineering session

### Goal

Turn the assigned specification into an offline, testable Pygame management game and assemble transparent evidence.

### Work completed

- Interpreted the mandatory mechanics and rubric.
- Defined a 12-round loop with two actions, four zones, seven tracked resources/values, nine JSON-driven events, delayed consequences, seeded replay, save/load, and five endings.
- Separated the Pygame scene/UI layer from the deterministic model and storage boundary.
- Added generated visuals and procedural tones, avoiding external copyrighted assets.
- Added start menu, instructions, map movement, dashboard, event cards, pause/restart/exit, mouse and keyboard paths, high contrast, and silent audio fallback.
- Built automated model, storage, data validation, UI-flow, and accessibility checks.
- Simulated 1,000 seeded games across five policies and retained raw CSV data.
- Captured four reproducible frames from the actual renderer.

### Decisions and reasons

- **Turn-based:** gives players time to reflect on moral/resource trade-offs and makes replay/test evidence exact.
- **Visible effects:** helps players understand responsibility and allows students to explain consequences during Q&A.
- **Delayed outcomes:** shows that environmental choices extend beyond immediate profit.
- **Balanced ending:** Ecology, Community, Hope, food, and water all matter; maximising one number is insufficient.
- **Generated assets:** ensures offline operation and removes licensing ambiguity.

### Failure analysis and fixes

The first package install targeted a read-only managed user directory. A local `.venv` resolved this and became the documented setup. The first direct `pytest` console command did not place the project root on its import path; using `python -m pytest` fixed test discovery. Audio is made optional because school hardware may not expose a mixer.

### Test result

Sixteen automated tests passed. The 1,000-run balance test showed pure extraction produced 200/200 neglect endings. No fixed policy guaranteed the highest faithful ending. Full counts and limitations are in `evidence/balance_report.txt`.

### Reflection

The most important technical insight is that UI and rules should be separated. The most important theme insight is that stewardship is not “nature points”: decisions connect creation, neighbour, trust, hope, and future scarcity. Human classroom testing is still necessary because automated strategies cannot measure clarity, fairness, or enjoyment.

## 17 November classroom playtest — student completion required

Record at least two real classmates, date/device, seed, route taken, ending, comments, observed confusion, FPS/technical issues, and changes made. Link the genuine unedited video. Do not invent results.

## 24 November final review — complete after real review

Record final student changes, full school-computer test, presentation rehearsal, member contributions, remaining limitations, signed theme confirmation, and final submission filenames.

## Evidence index

- Git history: four staged milestones (proposal, model, interface, validation/evidence).
- Architecture: `docs/ARCHITECTURE.md`
- Research: `docs/RESEARCH.md`
- Bug log: `docs/BUG_LOG.md`
- Test plan: `docs/TEST_PLAN.md`
- Automated results: `evidence/test_report.txt`
- Balance data: `evidence/balance_report.txt`, `evidence/balance_results.csv`
- Screenshots: `evidence/screenshots/`
- AI declaration: `docs/AI_USE_LOG.md`
- Meeting and contribution sources: `docs/MEETING_MINUTES.md`, `docs/CONTRIBUTION_LOG.md`

