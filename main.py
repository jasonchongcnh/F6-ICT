"""Entry point for Guardians of Creation."""

from __future__ import annotations

import argparse
import os
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Guardians of Creation Pygame")
    parser.add_argument("--seed", type=int, help="deterministic replay seed")
    parser.add_argument("--smoke-test", action="store_true", help="render a few frames and exit")
    parser.add_argument("--screenshot", type=Path, help="save the smoke-test frame")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.smoke_test:
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
        os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    from guardians.app import GameApp

    app = GameApp(seed=args.seed)
    return app.run(max_frames=3 if args.smoke_test else None, screenshot=args.screenshot)


if __name__ == "__main__":
    raise SystemExit(main())

