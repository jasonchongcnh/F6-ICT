# Bug and Iteration Log

| Date | ID | Symptom | Root cause | Resolution | Regression evidence | Status |
|---|---|---|---|---|---|---|
| 17 Nov 2026 | ENV-01 | `pip install` failed with read-only `/home/agent/.local/lib` | Managed cloud Python does not permit user-site writes | Created repository-local `.venv`; install and tests run there | Dependency install succeeded; complete suite executed | Closed |
| 17 Nov 2026 | TEST-01 | `pytest` executable could not import `guardians` | Console-script path did not include project root in this runtime | Standardised command as `python -m pytest` | All tests collected and passed | Closed |
| 17 Nov 2026 | UI-01 | Audio may be unavailable on some school devices | Mixer initialisation depends on hardware/driver | `TonePlayer` falls back to silent mode without stopping play | Headless UI test uses dummy audio | Closed |

Add actual classroom playtest issues below; never invent tester observations.

