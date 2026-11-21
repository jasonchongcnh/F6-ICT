"""《受造界守護者》程式入口。"""

from __future__ import annotations

import argparse
import os
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="《受造界守護者》Pygame 遊戲")
    parser.add_argument("--seed", type=int, help="固定重玩種子")
    parser.add_argument("--smoke-test", action="store_true", help="渲染數個畫面後離開")
    parser.add_argument("--screenshot", type=Path, help="儲存冒煙測試畫面")
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

