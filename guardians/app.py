"""Pygame 應用程式、場景、輸入、渲染及回饋。"""

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
        "忠信的好管家",
        "你同時關愛受造界與鄰人，使希望島欣欣向榮。你明智的犧牲守護了公益。",
    ),
    "solidarity": (
        "團結共融的社區",
        "信任與希望把全島連結起來。居民已準備好同心協力，繼續修復受造界。",
    ),
    "restoration": (
        "重現生機的島嶼",
        "森林與水源在耐心照料下逐漸復原。下一步，是更公平地分享這些恩賜。",
    ),
    "profit": (
        "短期利益的代價",
        "倉庫雖然充足，受造界或社區卻付出了代價。缺乏公義的繁榮無法維持公益。",
    ),
    "neglect": (
        "重新出發的召喚",
        "共同生活的一環被忽略了。希望仍在：反思、重來，並尋找更明智的平衡。",
    ),
}

ZONE_RECTS = {
    "forest": pygame.Rect(35, 195, 210, 145),
    "river": pygame.Rect(250, 195, 210, 145),
    "farm": pygame.Rect(35, 345, 210, 145),
    "village": pygame.Rect(250, 345, 210, 145),
}
ZONE_GRID = [["forest", "river"], ["farm", "village"]]
ZONE_LABELS = {"forest": "森林", "river": "河流", "farm": "農田", "village": "村莊"}


def load_chinese_font(size: int, *, bold: bool = False) -> pygame.font.Font:
    """選用可顯示繁體中文的系統字型，並在缺少時安全回退。"""
    names = "Noto Sans CJK TC,Microsoft JhengHei,Microsoft JhengHei UI,PingFang TC,Arial Unicode MS"
    path = pygame.font.match_font(names, bold=bold)
    return pygame.font.Font(path, size)


class TonePlayer:
    """小型原創程式化音效；沒有音訊裝置時自動靜音。"""

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
        pygame.display.set_caption("受造界守護者")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font_small = load_chinese_font(17)
        self.font = load_chinese_font(21)
        self.font_large = load_chinese_font(34, bold=True)
        self.font_title = load_chinese_font(48, bold=True)
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
        self.notify(f"新島嶼——重玩種子 {self.model.state.seed}")

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
                self.message = f"聲音：{'開啟' if self.tone.enabled else '關閉'}"
                self.message_timer = FPS * 2
                return
            if event.key == pygame.K_c:
                self.high_contrast = not self.high_contrast
                self.palette = HIGH_CONTRAST if self.high_contrast else COLORS
                self.message = f"高對比模式：{'開啟' if self.high_contrast else '關閉'}"
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
                self.notify("已載入島嶼存檔")
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
            self.notify("進度已儲存至 savegame.json")
        except ValueError as exc:
            self.notify(str(exc), False)

    def _load(self) -> None:
        try:
            self.model = load_game()
            self.scene = "event" if self.model.current_event else ("ending" if self.model.state.finished else "playing")
            self.notify("已載入遊戲進度")
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
        draw_text(self.screen, "受造界守護者", self.font_title, p["ink"], (400, 180), center=True)
        draw_text(self.screen, "好管家", self.font_large, p["forest"], (400, 232), center=True)
        labels = (("開始新的島嶼", "new"), ("載入島嶼存檔", "load"), ("遊戲說明", "instructions"), ("離開遊戲", "exit"))
        self.menu_buttons = []
        for index, (label, action) in enumerate(labels):
            button = Button(pygame.Rect(260, 278 + index * 58, 280, 44), label, action)
            button.draw(self.screen, self.font, p, focused=index == self.focus_index)
            self.menu_buttons.append(button)
        draw_text(self.screen, "C：高對比模式　　M：聲音開關", self.font_small, p["muted"], (400, 550), center=True)

    def _draw_instructions(self) -> None:
        p = self.palette
        draw_text(self.screen, "如何照顧希望島", self.font_large, p["ink"], (40, 35))
        sections = [
            ("你的使命", "在十二個回合內平衡生態、社區及希望。忠信的好管家會同時守護三者，並確保有足夠食物和食水。"),
            ("每個回合", "你有兩次行動。移動至四個區域之一，再選擇當地的一項行動。每回合結束時會出現事件，選擇可能帶來延後後果。"),
            ("操作方法", "WASD／方向鍵：選擇區域。1 或 2：執行行動。亦可全程使用滑鼠。Esc：暫停。F5：儲存。F9：載入。M：聲音。C：高對比。"),
            ("請緊記", "短期利益或能解決今天的問題，卻可能損害明天的公益。分享會消耗物資，但能建立信任與希望。遊戲沒有單一完美選擇。"),
        ]
        y = 95
        for heading, body in sections:
            draw_text(self.screen, heading, self.font, p["forest"], (55, y))
            y = draw_wrapped(self.screen, body, self.font, p["ink"], pygame.Rect(55, y + 28, 690, 90)) + 22
        draw_text(self.screen, "按畫面任何位置或按 Enter／Esc 返回", self.font, p["river"], (400, 565), center=True)

    def _draw_game(self) -> None:
        assert self.model is not None
        p = self.palette
        s = self.model.state
        draw_text(self.screen, "希望島", self.font_large, p["ink"], (25, 22))
        draw_text(self.screen, f"第 {min(s.round_number, MAX_ROUNDS)}／{MAX_ROUNDS} 回合　•　行動 {s.actions_left}", self.font, p["ink"], (475, 31))
        resources = (("食水", s.water, p["river"]), ("食物", s.food, p["farm"]), ("木材", s.wood, p["forest"]), ("信任", s.trust, p["village"]))
        for index, (label, value, color) in enumerate(resources):
            x = 25 + index * 190
            draw_text(self.screen, f"{label}: {value}", self.font, p["ink"], (x, 78))
            pygame.draw.rect(self.screen, color, (x, 104, min(150, value * 3 // 2), 8), border_radius=3)
        for zone, rect in ZONE_RECTS.items():
            color = p[zone]
            pygame.draw.rect(self.screen, color, rect, border_radius=15)
            border = 5 if zone == self.selected_zone else 2
            pygame.draw.rect(self.screen, p["ink"], rect, border, border_radius=15)
            draw_text(self.screen, ZONE_LABELS[zone], self.font_large, p["cream"], (rect.centerx, rect.top + 28), center=True)
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
        draw_text(self.screen, "公益儀表板", self.font, p["ink"], (500, 174))
        draw_bar(self.screen, "生態", s.ecology, pygame.Rect(500, 222, 250, 13), self.font_small, p, p["forest"])
        draw_bar(self.screen, "社區", s.community, pygame.Rect(500, 267, 250, 13), self.font_small, p, p["village"])
        draw_bar(self.screen, "希望", s.hope, pygame.Rect(500, 312, 250, 13), self.font_small, p, p["hope"])
        draw_text(self.screen, f"目前位置：{ZONE_LABELS[self.selected_zone]}", self.font, p["ink"], (500, 346))
        self.action_buttons = []
        for index, action in enumerate(ZONE_ACTIONS[self.selected_zone]):
            button = Button(pygame.Rect(500, 378 + index * 54, 250, 43), f"{index + 1}. {action['name']}", f"action-{index}", s.actions_left > 0)
            button.draw(self.screen, self.font_small, p)
            self.action_buttons.append(button)
        if s.history:
            draw_text(self.screen, "最新紀錄：" + s.history[-1][:54], self.font_small, p["muted"], (25, 516))
        draw_text(self.screen, "移動：WASD／方向鍵　•　選擇：1／2　•　Esc：暫停　•　F5／F9：儲存／載入", self.font_small, p["muted"], (25, 561))
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
        draw_text(self.screen, "島嶼抉擇", self.font_small, p["river"], (120, 98))
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
            draw_text(self.screen, choice.description[:85], self.font_small, p["cream"], (132, y + 37))
            y += 75

    def _draw_pause(self) -> None:
        p = self.palette
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 165))
        self.screen.blit(overlay, (0, 0))
        panel = pygame.Rect(235, 120, 330, 360)
        pygame.draw.rect(self.screen, p["panel"], panel, border_radius=18)
        draw_text(self.screen, "遊戲暫停", self.font_large, p["ink"], (400, 160), center=True)
        actions = (("繼續遊戲", "resume"), ("儲存進度", "save"), ("重新開始", "restart"), ("主選單", "menu"))
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
        draw_text(self.screen, f"生態 {s.ecology}　社區 {s.community}　希望 {s.hope}", self.font, p["ink"], (400, 375), center=True)
        self.menu_buttons = []
        for index, (label, action) in enumerate((("使用另一種子重玩", "restart"), ("返回主選單", "menu"))):
            button = Button(pygame.Rect(260, 425 + index * 58, 280, 44), label, action)
            button.draw(self.screen, self.font, p)
            self.menu_buttons.append(button)
        draw_text(self.screen, f"重玩種子：{s.seed}", self.font_small, p["muted"], (400, 560), center=True)

    def _draw_status_message(self) -> None:
        if not self.message or self.message_timer <= 0:
            return
        p = self.palette
        box = pygame.Rect(95, 540, 610, 40)
        pygame.draw.rect(self.screen, p["ink"], box, border_radius=8)
        draw_text(self.screen, self.message[:90], self.font_small, p["cream"], box.center, center=True)

