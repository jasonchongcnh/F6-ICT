import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from pathlib import Path

from guardians.app import GameApp, find_chinese_font_path, load_chinese_font


def test_chinese_font_is_a_real_font_file_and_renders_text():
    font_path = find_chinese_font_path()
    assert Path(font_path).is_file()
    font = load_chinese_font(24)
    rendered = font.render("受造界守護者", True, (0, 0, 0))
    assert rendered.get_width() > 60
    assert rendered.get_height() > 10


def test_macos_pingfang_path_is_preferred_when_present(monkeypatch):
    pingfang = "/System/Library/Fonts/PingFang.ttc"
    monkeypatch.setattr(Path, "is_file", lambda path: str(path) == pingfang)
    assert find_chinese_font_path() == pingfang


def test_menu_new_game_and_first_round_render():
    app = GameApp(seed=2026)
    app.new_game()
    assert app.scene == "playing"
    app.draw()
    app._take_action(1)
    app._take_action(1)
    assert app.scene == "event"
    app.draw()
    app._choose_event(0)
    assert app.scene in {"playing", "ending"}
    pygame.quit()


def test_accessibility_shortcuts_toggle_modes():
    app = GameApp(seed=1)
    contrast_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_c)
    sound_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_m)
    original_sound = app.tone.enabled
    app.handle_event(contrast_event)
    app.handle_event(sound_event)
    assert app.high_contrast is True
    assert app.tone.enabled is not original_sound
    pygame.quit()

