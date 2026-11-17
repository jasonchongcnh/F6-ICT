# Research, Benchmarks, and Trade-offs

Date: 17 November 2026

| Reference | Useful idea | Limitation for this project | Decision |
|---|---|---|---|
| *Reigns* | Short event cards make consequences easy to understand | Binary swipes can hide system depth | Use concise event cards, but show exact resource/value effects |
| *Mini Metro* | Clean visual language and systems that interact | Real-time pressure could reduce reflection | Use a calm turn-based structure and readable dashboard |
| *Frostpunk* | Moral choices connect survival and community values | Tone and complexity are too severe for the audience | Keep dilemmas age-appropriate and hopeful; sacrifice matters without graphic content |

## Main trade-offs

- **Turn-based over timed:** easier to explain, test, save, and make accessible; less action-oriented.
- **Generated shapes over downloaded art:** entirely original and offline-safe; less visually detailed.
- **Visible numeric effects over hidden outcomes:** supports learning and verification; reduces mystery.
- **Seeded randomness:** enables replay and exact bug reproduction while preserving variety.
- **JSON event data:** non-programmers can tune content; validation code is required to prevent malformed events.

