"""Shared configuration constants."""

from pathlib import Path

WIDTH = 800
HEIGHT = 600
FPS = 60
MAX_ROUNDS = 12
ACTIONS_PER_ROUND = 2
MIN_VALUE = 0
MAX_VALUE = 100

ROOT = Path(__file__).resolve().parent.parent
EVENTS_PATH = ROOT / "data" / "events.json"
DEFAULT_SAVE_PATH = ROOT / "savegame.json"

COLORS = {
    "cream": (247, 241, 218),
    "ink": (31, 45, 38),
    "forest": (54, 112, 68),
    "river": (61, 143, 184),
    "farm": (205, 161, 69),
    "village": (177, 105, 83),
    "hope": (232, 184, 64),
    "danger": (188, 64, 58),
    "panel": (255, 252, 239),
    "muted": (101, 112, 103),
}

HIGH_CONTRAST = {
    "cream": (0, 0, 0),
    "ink": (255, 255, 255),
    "forest": (0, 210, 90),
    "river": (0, 180, 255),
    "farm": (255, 220, 0),
    "village": (255, 100, 160),
    "hope": (255, 255, 0),
    "danger": (255, 80, 80),
    "panel": (20, 20, 20),
    "muted": (210, 210, 210),
}

