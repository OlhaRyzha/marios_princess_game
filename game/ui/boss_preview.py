from collections.abc import Callable
from pathlib import Path

import pygame

from game.data.bosses import BossConfig
from game.i18n import Localizer
from game.utils.constants import FONT_SIZE, HEIGHT, WIDTH
from game.utils.fonts import load_font
from game.utils.images import load_image

PADDING = 24
CARD_W = int(WIDTH * 0.78)
CARD_H = int(HEIGHT * 0.64)


class BossPreview:

    def __init__(
        self,
        font: "pygame.font.Font",
        localizer: Localizer | None = None,
        on_select: Callable[[BossConfig], None] | None = None,
    ):
        self.font = font
        self.localizer = localizer or Localizer()
        self.active = False
        self._items: list[BossConfig] = []
        self._idx = 0
        self._img_cache: dict[Path, pygame.Surface] = {}
        self.title_font = load_font(int(FONT_SIZE * 1.4))
        self.small = load_font(int(FONT_SIZE * 0.9))
        self.on_select = on_select

    def open(self, bosses: tuple[BossConfig, ...]) -> None:
        self._items = list(bosses)
        self._idx = 0
        self.active = bool(self._items)

    def is_done(self) -> bool:
        return not self.active

    def _wrap(self, text: str, max_w: int) -> "list[pygame.Surface]":
        words = text.split()
        lines: list[str] = []
        cur = ""
        for w in words:
            test = (cur + " " + w).strip()
            if self.font.size(test)[0] <= max_w:
                cur = test
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        return [self.font.render(line, True, (25, 25, 25)) for line in lines]

    def handle_key(self, event: "pygame.event.Event"):
        if not self.active:
            return
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RIGHT, pygame.K_d):
                self._idx = (self._idx + 1) % len(self._items)
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                self._idx = (self._idx - 1) % len(self._items)
            elif event.key == pygame.K_SPACE:
                self._idx = (self._idx + 1) % len(self._items)
            elif event.key == pygame.K_RETURN:
                if self.on_select:
                    self.on_select(self._items[self._idx])
                self.active = False
            elif event.key == pygame.K_ESCAPE:
                self.active = False

    def draw(self, surface: "pygame.Surface"):
        if not self.active or not self._items:
            return
        data = self._items[self._idx]
        card, inner = self._draw_card(surface)
        text_area = pygame.Rect(inner.x, inner.y, int(inner.w * 0.56), inner.h)
        self._draw_description(surface, data, text_area)
        self._draw_navigation(surface, card, inner, text_area)
        self._draw_boss_image(surface, data, inner, text_area)

    def _draw_card(self, surface: pygame.Surface) -> tuple[pygame.Rect, pygame.Rect]:
        """Draw the modal backdrop and return its content rectangles."""
        dark = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        dark.fill((10, 18, 26, 180))
        surface.blit(dark, (0, 0))

        card = pygame.Rect(
            (WIDTH - CARD_W) // 2, (HEIGHT - CARD_H) // 2, CARD_W, CARD_H
        )
        pygame.draw.rect(surface, (235, 238, 245), card, border_radius=16)
        pygame.draw.rect(surface, (40, 60, 85), card, width=3, border_radius=16)
        return card, card.inflate(-PADDING * 2, -PADDING * 2)

    def _draw_description(
        self, surface: pygame.Surface, data: BossConfig, text_area: pygame.Rect
    ) -> None:
        """Draw the boss title and localized strategy sections."""
        title = self.title_font.render(data.name, True, (30, 40, 60))
        surface.blit(title, (text_area.x, text_area.y))

        y = text_area.y + title.get_height() + 12
        sections = (
            (self.localizer.text("boss.about"), self.localizer.resolve(data.about)),
            (
                self.localizer.text("boss.strategy"),
                self.localizer.resolve(data.strategy),
            ),
            (self.localizer.text("boss.goal"), self.localizer.resolve(data.goal)),
        )
        for label, text in sections:
            lab = self.small.render(label, True, (60, 70, 90))
            surface.blit(lab, (text_area.x, y))
            y += lab.get_height() + 4
            for ln in self._wrap(text, text_area.w):
                surface.blit(ln, (text_area.x, y))
                y += ln.get_height() + 2
            y += 8

    def _draw_navigation(
        self,
        surface: pygame.Surface,
        card: pygame.Rect,
        inner: pygame.Rect,
        text_area: pygame.Rect,
    ) -> None:
        """Draw keyboard help and the current page number."""
        hint = self.small.render(
            self.localizer.text("boss.hint"),
            True,
            (80, 90, 110),
        )
        surface.blit(hint, (text_area.x, inner.bottom - hint.get_height()))
        page = self.small.render(
            f"{self._idx + 1}/{len(self._items)}", True, (80, 90, 110)
        )
        surface.blit(
            page,
            (card.right - page.get_width() - 10, card.bottom - page.get_height() - 8),
        )

    def _draw_boss_image(
        self,
        surface: pygame.Surface,
        data: BossConfig,
        inner: pygame.Rect,
        text_area: pygame.Rect,
    ) -> None:
        """Load, cache, and draw the selected boss image."""
        img_area = pygame.Rect(
            text_area.right + 18, inner.y, inner.right - text_area.right - 18, inner.h
        )
        path = data.image_path
        img = self._img_cache.get(path)
        if img is None:
            raw = load_image(path)
            max_w = img_area.w
            max_h = img_area.h
            iw, ih = raw.get_size()
            scale = min(max_w / iw, max_h / ih, 1.0)
            img = pygame.transform.smoothscale(raw, (int(iw * scale), int(ih * scale)))
            self._img_cache[path] = img
        rect = img.get_rect(center=img_area.center)
        surface.blit(img, rect)
