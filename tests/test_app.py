import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from guardians.app import GameApp


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

