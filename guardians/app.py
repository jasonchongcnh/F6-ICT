"""Pygame application, scenes, input, rendering, and feedback."""

from __future__ import annotations

import array
import math
import os
import random
from pathlib import Path

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pygame

from .config import COLORS, FPS, HEIGHT, HIGH_CONTRAST, MAX_ROUNDS, WIDTH
from .model import GameModel, ZONE_ACTIONS
from .storage import load_game, save_game
from .ui import Button, draw_bar, draw_text, draw_wrapped

ENDING_COPY = {
    "faithful": (
        "Faithful Steward",
        "Haven Island flourishes because creation and neighbours were cared for together. Your prudent sacrifices served the common good.",
    ),
    "solidarity": (
        "A Community of Solidarity",
        "Trust and hope bind the island together. The people are ready to continue restoring creation as one community.",
    ),
    "restoration": (
        "The Living Island",
        "Forests and waters recover through patient care. The next task is to share those gifts even more fairly.",
    ),
    "profit": (
        "The Price of Quick Profit",
        "Stores are full, but creation or community paid the cost. Prosperity without justice cannot sustain the common good.",
    ),
    "neglect": (
        "A Call to Begin Again",
        "One part of shared life was neglected. Hope remains: reflect, restart, and seek a wiser balance.",
    ),
}

ZONE_RECTS = {
    "forest": pygame.Rect(35, 195, 210, 145),
    "river": pygame.Rect(250, 195, 210, 145),
    "farm": pygame.Rect(35, 345, 210, 145),
    "village": pygame.Rect(250, 345, 210, 145),
}
ZONE_GRID = [["forest", "river"], ["farm", "village"]]


class TonePlayer:
    """Small original procedural sound effects; gracefully silent without audio."""

    def __init__(self) -> None:
        self.enabled = True
        self.sounds: dict[str, pygame.mixer.Sound] = {}
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=1)
            self.sounds = {
                "good": self._tone(660, 0.10),
                "bad": self._tone(180, 0.14),
                "click": self._tone(440, 0.06),
            }
        except pygame.error:
            self.enabled = False

    @staticmethod
    def _tone(frequency: int, duration: float) -> pygame.mixer.Sound:
        sample_rate = 22050
        samples = array.array("h")
        count = int(sample_rate * duration)
        for index in range(count):
            fade = 1 - index / count
            value = int(5000 * fade * math.sin(2 * math.pi * frequency * index / sample_rate))
            samples.append(value)
        return pygame.mixer.Sound(buffer=samples)

    def play(self, name: str) -> None:
        if self.enabled and name in self.sounds:
            self.sounds[name].play()


class GameApp:
    def __init__(self, *, seed: int | None = None) -> None:
        pygame.init()
        pygame.display.set_caption("Guardians of Creation")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font_small = pygame.font.Font(None, 20)
        self.font = pygame.font.Font(None, 25)
        self.font_large = pygame.font.Font(None, 42)
        self.font_title = pygame.font.Font(None, 59)
        self.running = True
        self.scene = "menu"
        self.model: GameModel | None = None
        self.seed_override = seed
        self.high_contrast = False
        self.palette = COLORS
        self.tone = TonePlayer()
        self.message = ""
        self.message_timer = 0
        self.focus_index = 0
        self.selected_zone = "village"
        self.action_buttons: list[Button] = []
        self.menu_buttons: list[Button] = []
        self._particles: list[dict[str, float]] = []

    def new_game(self) -> None:
        self.model = GameModel(seed=self.seed_override)
        self.scene = "playing"
        self.selected_zone = "village"
        self.focus_index = 0
        self.notify(f"New island — replay seed {self.model.state.seed}")

    def notify(self, message: str, positive: bool = True) -> None:
        self.message = message
        self.message_timer = FPS * 3
        self.tone.play("good" if positive else "bad")
        for _ in range(16):
            self._particles.append({
                "x": random.uniform(500, 770),
                "y": random.uniform(155, 500),
                "vx": random.uniform(-0.4, 0.4),
                "vy": random.uniform(-1.5, -0.4),
                "life": random.uniform(25, 55),
                "good": 1.0 if positive else 0.0,
            })

    def run(self, *, max_frames: int | None = None, screenshot: Path | None = None) -> int:
        frames = 0
        while self.running:
            for event in pygame.event.get():
                self.handle_event(event)
            self.update()
            self.draw()
            pygame.display.flip()
            frames += 1
            if max_frames is not None and frames >= max_frames:
                if screenshot:
                    screenshot.parent.mkdir(parents=True, exist_ok=True)
                    pygame.image.save(self.screen, screenshot)
                break
            self.clock.tick(FPS)
        pygame.quit()
        return 0

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT:
            self.running = False
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                self.tone.enabled = not self.tone.enabled
                self.message = f"Sound {'on' if self.tone.enabled else 'off'}"
                self.message_timer = FPS * 2
                return
            if event.key == pygame.K_c:
                self.high_contrast = not self.high_contrast
                self.palette = HIGH_CONTRAST if self.high_contrast else COLORS
                self.message = f"High contrast {'on' if self.high_contrast else 'off'}"
                self.message_timer = FPS * 2
                return

        if self.scene == "menu":
            self._menu_event(event)
        elif self.scene == "instructions":
            if (event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_RETURN)) or event.type == pygame.MOUSEBUTTONDOWN:
                self.scene = "menu"
        elif self.scene == "playing":
            self._playing_event(event)
        elif self.scene == "event":
            self._event_card_event(event)
        elif self.scene == "paused":
            self._pause_event(event)
        elif self.scene == "ending":
            self._ending_event(event)

    def _menu_event(self, event: pygame.event.Event) -> None:
        for button in self.menu_buttons:
            if button.clicked(event):
                self._menu_action(button.action)
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_DOWN, pygame.K_s):
                self.focus_index = (self.focus_index + 1) % 4
            elif event.key in (pygame.K_UP, pygame.K_w):
                self.focus_index = (self.focus_index - 1) % 4
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._menu_action(("new", "load", "instructions", "exit")[self.focus_index])

    def _menu_action(self, action: str) -> None:
        self.tone.play("click")
        if action == "new":
            self.new_game()
        elif action == "load":
            try:
                self.model = load_game()
                self.scene = "event" if self.model.current_event else ("ending" if self.model.state.finished else "playing")
                self.notify("Saved island loaded")
            except ValueError as exc:
                self.notify(str(exc), False)
        elif action == "instructions":
            self.scene = "instructions"
        elif action == "exit":
            self.running = False

    def _playing_event(self, event: pygame.event.Event) -> None:
        assert self.model is not None
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.scene = "paused"
                return
            if event.key == pygame.K_F5:
                self._save()
                return
            if event.key == pygame.K_F9:
                self._load()
                return
            row, column = next((r, c) for r, line in enumerate(ZONE_GRID) for c, zone in enumerate(line) if zone == self.selected_zone)
            if event.key in (pygame.K_LEFT, pygame.K_a):
                column = max(0, column - 1)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                column = min(1, column + 1)
            elif event.key in (pygame.K_UP, pygame.K_w):
                row = max(0, row - 1)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                row = min(1, row + 1)
            elif event.key in (pygame.K_1, pygame.K_KP1):
                self._take_action(0)
                return
            elif event.key in (pygame.K_2, pygame.K_KP2, pygame.K_RETURN, pygame.K_SPACE):
                self._take_action(1)
                return
            self.selected_zone = ZONE_GRID[row][column]
            self.model.state.current_zone = self.selected_zone
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for zone, rect in ZONE_RECTS.items():
                if rect.collidepoint(event.pos):
                    self.selected_zone = zone
                    self.model.state.current_zone = zone
                    return
            for index, button in enumerate(self.action_buttons):
                if button.clicked(event):
                    self._take_action(index)

    def _take_action(self, index: int) -> None:
        assert self.model is not None
        try:
            effects = ZONE_ACTIONS[self.selected_zone][index]["effects"]
            message = self.model.perform_zone_action(self.selected_zone, index)
            self.notify(message, sum(effects.values()) >= 0)
            if self.model.state.finished:
                self.scene = "ending"
            elif self.model.current_event:
                self.scene = "event"
                self.focus_index = 0
        except ValueError as exc:
            self.notify(str(exc), False)

    def _event_card_event(self, event: pygame.event.Event) -> None:
        assert self.model is not None and self.model.current_event is not None
        choices = self.model.current_event.choices
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_DOWN, pygame.K_s):
                self.focus_index = (self.focus_index + 1) % len(choices)
            elif event.key in (pygame.K_UP, pygame.K_w):
                self.focus_index = (self.focus_index - 1) % len(choices)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._choose_event(self.focus_index)
            elif pygame.K_1 <= event.key <= pygame.K_4:
                index = event.key - pygame.K_1
                if index < len(choices):
                    self._choose_event(index)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for index, button in enumerate(self.action_buttons):
                if button.clicked(event):
                    self._choose_event(index)

    def _choose_event(self, index: int) -> None:
        assert self.model is not None
        event = self.model.current_event
        assert event is not None
        effects = event.choices[index].effects
        message = self.model.choose_event(index)
        self.notify(message, sum(effects.values()) >= 0)
        self.scene = "ending" if self.model.state.finished else "playing"

    def _pause_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.scene = "playing"
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for button in self.menu_buttons:
                if button.clicked(event):
                    if button.action == "resume":
                        self.scene = "playing"
                    elif button.action == "save":
                        self._save()
                    elif button.action == "restart":
                        self.new_game()
                    elif button.action == "menu":
                        self.scene = "menu"

    def _ending_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_r, pygame.K_RETURN):
                self.new_game()
            elif event.key in (pygame.K_ESCAPE, pygame.K_m):
                self.scene = "menu"
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for button in self.menu_buttons:
                if button.clicked(event):
                    self.new_game() if button.action == "restart" else setattr(self, "scene", "menu")

    def _save(self) -> None:
        assert self.model is not None
        try:
            save_game(self.model)
            self.notify("Progress saved to savegame.json")
        except ValueError as exc:
            self.notify(str(exc), False)

    def _load(self) -> None:
        try:
            self.model = load_game()
            self.scene = "event" if self.model.current_event else ("ending" if self.model.state.finished else "playing")
            self.notify("Saved progress loaded")
        except ValueError as exc:
            self.notify(str(exc), False)

    def update(self) -> None:
        if self.message_timer > 0:
            self.message_timer -= 1
        for particle in self._particles:
            particle["x"] += particle["vx"]
            particle["y"] += particle["vy"]
            particle["life"] -= 1
        self._particles = [particle for particle in self._particles if particle["life"] > 0]

    def draw(self) -> None:
        self.screen.fill(self.palette["cream"])
        if self.scene == "menu":
            self._draw_menu()
        elif self.scene == "instructions":
            self._draw_instructions()
        elif self.scene in ("playing", "paused"):
            self._draw_game()
            if self.scene == "paused":
                self._draw_pause()
        elif self.scene == "event":
            self._draw_game()
            self._draw_event_card()
        elif self.scene == "ending":
            self._draw_ending()
        self._draw_status_message()

    def _draw_menu(self) -> None:
        p = self.palette
        pygame.draw.circle(self.screen, p["river"], (400, 98), 60)
        pygame.draw.circle(self.screen, p["forest"], (375, 88), 26)
        pygame.draw.circle(self.screen, p["farm"], (425, 112), 20)
        draw_text(self.screen, "GUARDIANS OF CREATION", self.font_title, p["ink"], (400, 180), center=True)
        draw_text(self.screen, "The Good Steward", self.font_large, p["forest"], (400, 224), center=True)
        labels = (("Begin a New Island", "new"), ("Load Saved Island", "load"), ("How to Play", "instructions"), ("Exit", "exit"))
        self.menu_buttons = []
        for index, (label, action) in enumerate(labels):
            button = Button(pygame.Rect(260, 278 + index * 58, 280, 44), label, action)
            button.draw(self.screen, self.font, p, focused=index == self.focus_index)
            self.menu_buttons.append(button)
        draw_text(self.screen, "C: high contrast   M: sound", self.font_small, p["muted"], (400, 550), center=True)

    def _draw_instructions(self) -> None:
        p = self.palette
        draw_text(self.screen, "How to Care for Haven Island", self.font_large, p["ink"], (40, 35))
        sections = [
            ("Your mission", "Balance Ecology, Community, and Hope for 12 rounds. A faithful steward protects all three while keeping enough food and water."),
            ("Each round", "You have two actions. Move across the four zones, then choose one of its two actions. An event follows every round; choices may have delayed consequences."),
            ("Controls", "WASD / arrows: select zone. 1 or 2: action. Mouse works throughout. Esc: pause. F5: save. F9: load. M: sound. C: high contrast."),
            ("Remember", "Quick profit may solve today's problem but harm the common good tomorrow. Sharing can cost supplies while building trust and hope. There is no single perfect choice."),
        ]
        y = 95
        for heading, body in sections:
            draw_text(self.screen, heading, self.font, p["forest"], (55, y))
            y = draw_wrapped(self.screen, body, self.font, p["ink"], pygame.Rect(55, y + 28, 690, 90)) + 22
        draw_text(self.screen, "Click anywhere or press Enter / Esc to return", self.font, p["river"], (400, 565), center=True)

    def _draw_game(self) -> None:
        assert self.model is not None
        p = self.palette
        s = self.model.state
        draw_text(self.screen, "Haven Island", self.font_large, p["ink"], (25, 22))
        draw_text(self.screen, f"Round {min(s.round_number, MAX_ROUNDS)} / {MAX_ROUNDS}  •  Actions {s.actions_left}", self.font, p["ink"], (475, 31))
        resources = (("Water", s.water, p["river"]), ("Food", s.food, p["farm"]), ("Wood", s.wood, p["forest"]), ("Trust", s.trust, p["village"]))
        for index, (label, value, color) in enumerate(resources):
            x = 25 + index * 190
            draw_text(self.screen, f"{label}: {value}", self.font, p["ink"], (x, 78))
            pygame.draw.rect(self.screen, color, (x, 104, min(150, value * 3 // 2), 8), border_radius=3)
        for zone, rect in ZONE_RECTS.items():
            color = p[zone]
            pygame.draw.rect(self.screen, color, rect, border_radius=15)
            border = 5 if zone == self.selected_zone else 2
            pygame.draw.rect(self.screen, p["ink"], rect, border, border_radius=15)
            draw_text(self.screen, zone.title(), self.font_large, p["cream"], (rect.centerx, rect.top + 28), center=True)
            icon_y = rect.top + 84
            if zone == "forest":
                pygame.draw.polygon(self.screen, p["cream"], [(rect.centerx, icon_y - 32), (rect.centerx - 28, icon_y + 20), (rect.centerx + 28, icon_y + 20)])
                pygame.draw.rect(self.screen, p["ink"], (rect.centerx - 4, icon_y + 17, 8, 22))
            elif zone == "river":
                for offset in (-14, 6, 26):
                    pygame.draw.arc(self.screen, p["cream"], (rect.centerx - 40, icon_y + offset - 20, 80, 24), math.pi, math.tau, 4)
            elif zone == "farm":
                for offset in (-22, 0, 22):
                    pygame.draw.line(self.screen, p["cream"], (rect.centerx + offset, icon_y - 24), (rect.centerx + offset, icon_y + 30), 4)
                    pygame.draw.circle(self.screen, p["cream"], (rect.centerx + offset - 7, icon_y - 8), 6)
            else:
                pygame.draw.polygon(self.screen, p["cream"], [(rect.centerx - 35, icon_y), (rect.centerx, icon_y - 30), (rect.centerx + 35, icon_y)])
                pygame.draw.rect(self.screen, p["cream"], (rect.centerx - 27, icon_y, 54, 35))
        # Player marker moves between actual interactive zones.
        marker = ZONE_RECTS[self.selected_zone]
        pygame.draw.circle(self.screen, p["hope"], (marker.right - 23, marker.bottom - 22), 12)
        pygame.draw.circle(self.screen, p["ink"], (marker.right - 23, marker.bottom - 22), 12, 2)

        panel = pygame.Rect(480, 155, 295, 370)
        pygame.draw.rect(self.screen, p["panel"], panel, border_radius=14)
        pygame.draw.rect(self.screen, p["ink"], panel, 2, border_radius=14)
        draw_text(self.screen, "Common Good Dashboard", self.font, p["ink"], (500, 174))
        draw_bar(self.screen, "Ecology", s.ecology, pygame.Rect(500, 222, 250, 13), self.font_small, p, p["forest"])
        draw_bar(self.screen, "Community", s.community, pygame.Rect(500, 267, 250, 13), self.font_small, p, p["village"])
        draw_bar(self.screen, "Hope", s.hope, pygame.Rect(500, 312, 250, 13), self.font_small, p, p["hope"])
        draw_text(self.screen, f"At the {self.selected_zone.title()}", self.font, p["ink"], (500, 346))
        self.action_buttons = []
        for index, action in enumerate(ZONE_ACTIONS[self.selected_zone]):
            button = Button(pygame.Rect(500, 378 + index * 54, 250, 43), f"{index + 1}. {action['name']}", f"action-{index}", s.actions_left > 0)
            button.draw(self.screen, self.font_small, p)
            self.action_buttons.append(button)
        if s.history:
            draw_text(self.screen, "Latest: " + s.history[-1][:82], self.font_small, p["muted"], (25, 516))
        draw_text(self.screen, "Move: WASD/arrows  •  Choose: 1/2  •  Esc: pause  •  F5/F9: save/load", self.font_small, p["muted"], (25, 561))
        for particle in self._particles:
            color = p["hope"] if particle["good"] else p["danger"]
            pygame.draw.circle(self.screen, color, (int(particle["x"]), int(particle["y"])), 3)

    def _draw_event_card(self) -> None:
        assert self.model is not None and self.model.current_event is not None
        p = self.palette
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        card = pygame.Rect(90, 72, 620, 470)
        pygame.draw.rect(self.screen, p["panel"], card, border_radius=18)
        pygame.draw.rect(self.screen, p["ink"], card, 3, border_radius=18)
        event = self.model.current_event
        draw_text(self.screen, "ISLAND DECISION", self.font_small, p["river"], (120, 98))
        draw_text(self.screen, event.title, self.font_large, p["ink"], (120, 125))
        draw_wrapped(self.screen, event.text, self.font, p["ink"], pygame.Rect(120, 173, 560, 70))
        self.action_buttons = []
        y = 248
        for index, choice in enumerate(event.choices):
            effects = GameModel.describe_effects(choice.effects)
            label = f"{index + 1}. {choice.label} — {effects}"
            button = Button(pygame.Rect(120, y, 560, 58), label, f"choice-{index}")
            button.draw(self.screen, self.font_small, p, focused=index == self.focus_index)
            self.action_buttons.append(button)
            draw_text(self.screen, choice.description[:85], self.font_small, p["muted"], (132, y + 37))
            y += 75

    def _draw_pause(self) -> None:
        p = self.palette
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 165))
        self.screen.blit(overlay, (0, 0))
        panel = pygame.Rect(235, 120, 330, 360)
        pygame.draw.rect(self.screen, p["panel"], panel, border_radius=18)
        draw_text(self.screen, "Paused", self.font_large, p["ink"], (400, 160), center=True)
        actions = (("Resume", "resume"), ("Save Progress", "save"), ("Restart", "restart"), ("Main Menu", "menu"))
        self.menu_buttons = []
        for index, (label, action) in enumerate(actions):
            button = Button(pygame.Rect(275, 207 + index * 58, 250, 43), label, action)
            button.draw(self.screen, self.font, p)
            self.menu_buttons.append(button)

    def _draw_ending(self) -> None:
        assert self.model is not None and self.model.state.ending is not None
        p = self.palette
        ending = self.model.state.ending
        title, body = ENDING_COPY[ending]
        accent = p["danger"] if ending in ("profit", "neglect") else p["forest"]
        pygame.draw.circle(self.screen, accent, (400, 120), 70)
        pygame.draw.circle(self.screen, p["hope"], (400, 120), 42, 5)
        draw_text(self.screen, title, self.font_title, p["ink"], (400, 220), center=True)
        draw_wrapped(self.screen, body, self.font, p["ink"], pygame.Rect(140, 260, 520, 100))
        s = self.model.state
        draw_text(self.screen, f"Ecology {s.ecology}   Community {s.community}   Hope {s.hope}", self.font, p["ink"], (400, 375), center=True)
        self.menu_buttons = []
        for index, (label, action) in enumerate((("Try Another Seed", "restart"), ("Main Menu", "menu"))):
            button = Button(pygame.Rect(260, 425 + index * 58, 280, 44), label, action)
            button.draw(self.screen, self.font, p)
            self.menu_buttons.append(button)
        draw_text(self.screen, f"Replay seed: {s.seed}", self.font_small, p["muted"], (400, 560), center=True)

    def _draw_status_message(self) -> None:
        if not self.message or self.message_timer <= 0:
            return
        p = self.palette
        box = pygame.Rect(95, 540, 610, 40)
        pygame.draw.rect(self.screen, p["ink"], box, border_radius=8)
        draw_text(self.screen, self.message[:90], self.font_small, p["cream"], box.center, center=True)

