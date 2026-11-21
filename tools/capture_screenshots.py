"""從實際 Pygame 渲染器擷取可重現畫面。"""

from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from guardians.app import GameApp


def save(app: GameApp, path: Path) -> None:
    app.draw()
    pygame.display.flip()
    pygame.image.save(app.screen, path)


def main() -> int:
    output = Path("evidence/screenshots")
    output.mkdir(parents=True, exist_ok=True)
    app = GameApp(seed=20261117)
    save(app, output / "01_main_menu.png")
    app.new_game()
    save(app, output / "02_gameplay_dashboard.png")
    app._take_action(1)
    app.selected_zone = "river"
    app._take_action(1)
    save(app, output / "03_event_decision.png")
    app.model.state.ending = "faithful"
    app.model.state.finished = True
    app.scene = "ending"
    app.message_timer = 0
    save(app, output / "04_faithful_ending.png")
    pygame.quit()
    print(f"已在 {output} 擷取 4 張截圖")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

