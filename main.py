"""《受造界守護者》程式入口。"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="《受造界守護者》Pygame 遊戲")
    parser.add_argument("--seed", type=int, help="固定重玩種子")
    parser.add_argument("--smoke-test", action="store_true", help="渲染數個畫面後離開")
    parser.add_argument("--screenshot", type=Path, help="儲存冒煙測試畫面")
    return parser.parse_args()


def validate_python_version(version_info: tuple[int, int] | object = sys.version_info) -> None:
    """Pygame CE 2.5.6 支援本專題採用的 Python 3.11–3.13。"""
    major, minor = version_info[0], version_info[1]  # type: ignore[index]
    if (major, minor) < (3, 11) or (major, minor) >= (3, 14):
        raise SystemExit(
            "此遊戲需要 Python 3.11、3.12 或 3.13。\n"
            f"目前版本：Python {major}.{minor}\n\n"
            "macOS：請在專題資料夾執行 ./setup_macos.command，"
            "或先安裝 Python 3.12 再建立虛擬環境。\n"
            "請勿使用目前不相容的 Anaconda Python 3.14 執行 Pygame CE 2.5.6。"
        )


def main() -> int:
    validate_python_version()
    args = parse_args()
    if args.smoke_test:
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
        os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    try:
        from guardians.app import GameApp
    except (ImportError, NotImplementedError) as exc:
        if "font" in str(exc).lower() or "pygame" in str(exc).lower():
            raise SystemExit(
                "Pygame 圖像／字型模組無法載入。\n"
                "請在專題資料夾執行 ./setup_macos.command，然後使用：\n"
                "  .venv-mac/bin/python main.py\n\n"
                f"原始錯誤：{exc}"
            ) from exc
        raise

    app = GameApp(seed=args.seed)
    return app.run(max_frames=3 if args.smoke_test else None, screenshot=args.screenshot)


if __name__ == "__main__":
    raise SystemExit(main())

