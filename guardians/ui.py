"""Reusable Pygame drawing and interaction helpers."""

from __future__ import annotations

from dataclasses import dataclass

import pygame


def wrap_text(text: str, font: pygame.font.Font, width: int) -> list[str]:
    """Wrap text by measured pixel width."""
    lines: list[str] = []
    for paragraph in text.splitlines() or [""]:
        words = paragraph.split()
        current = ""
        for word in words:
            candidate = f"{current} {word}".strip()
            if current and font.size(candidate)[0] > width:
                lines.append(current)
                current = word
            else:
                current = candidate
        lines.append(current)
    return lines


def draw_text(
    surface: pygame.Surface,
    text: str,
    font: pygame.font.Font,
    color: pygame.Color | tuple[int, int, int],
    pos: tuple[int, int],
    *,
    center: bool = False,
) -> pygame.Rect:
    rendered = font.render(text, True, color)
    rect = rendered.get_rect(center=pos) if center else rendered.get_rect(topleft=pos)
    surface.blit(rendered, rect)
    return rect


def draw_wrapped(
    surface: pygame.Surface,
    text: str,
    font: pygame.font.Font,
    color: tuple[int, int, int],
    rect: pygame.Rect,
    line_gap: int = 3,
) -> int:
    y = rect.top
    for line in wrap_text(text, font, rect.width):
        surface.blit(font.render(line, True, color), (rect.left, y))
        y += font.get_linesize() + line_gap
    return y


@dataclass
class Button:
    rect: pygame.Rect
    label: str
    action: str
    enabled: bool = True

    def draw(
        self,
        surface: pygame.Surface,
        font: pygame.font.Font,
        palette: dict[str, tuple[int, int, int]],
        *,
        focused: bool = False,
    ) -> None:
        hovered = self.rect.collidepoint(pygame.mouse.get_pos())
        color = palette["forest"] if self.enabled else palette["muted"]
        if hovered or focused:
            color = palette["river"]
        pygame.draw.rect(surface, color, self.rect, border_radius=9)
        pygame.draw.rect(surface, palette["ink"], self.rect, 2 if focused else 1, border_radius=9)
        text_color = palette["cream"] if self.enabled else palette["panel"]
        draw_text(surface, self.label, font, text_color, self.rect.center, center=True)

    def clicked(self, event: pygame.event.Event) -> bool:
        return bool(
            self.enabled
            and event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )


def draw_bar(
    surface: pygame.Surface,
    label: str,
    value: int,
    rect: pygame.Rect,
    font: pygame.font.Font,
    palette: dict[str, tuple[int, int, int]],
    color: tuple[int, int, int],
) -> None:
    draw_text(surface, f"{label} {value}", font, palette["ink"], (rect.left, rect.top - 18))
    pygame.draw.rect(surface, palette["muted"], rect, border_radius=4)
    fill = rect.copy()
    fill.width = max(0, round(rect.width * value / 100))
    pygame.draw.rect(surface, color if value > 25 else palette["danger"], fill, border_radius=4)
    pygame.draw.rect(surface, palette["ink"], rect, 1, border_radius=4)

