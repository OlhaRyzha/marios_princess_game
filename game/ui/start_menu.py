import logging
import os
from collections.abc import Sequence

import pygame

from game.actions import MenuAction, MenuItem
from game.data.start_menu import MAIN_MENU_ITEMS
from game.i18n import LocalizedText, Localizer
from game.utils.constants import BACKGROUNDS_DIR, FONT_SIZE, HEIGHT, WIDTH
from game.utils.fonts import load_font

MENU_BG_PATH = os.path.join(BACKGROUNDS_DIR, "mushroom_woods", "sky.png")
logger = logging.getLogger(__name__)

TITLE_TEXT = "Mario’s Princess"

BTN_HEIGHT = 70
BTN_WIDTH_RATIO = 0.46
BTN_GAP = 20
TITLE_Y = int(HEIGHT * 0.15)

ColorTuple = tuple[int, int, int] | tuple[int, int, int, int]
ColorValue = pygame.Color | ColorTuple


def _load_image(path: str) -> pygame.Surface:
    try:
        img = pygame.image.load(path).convert_alpha()
    except (FileNotFoundError, OSError, pygame.error) as e:
        logger.warning("Could not load menu background %s: %s", path, e)
        img = pygame.Surface((WIDTH, HEIGHT))
        img.fill((255, 200, 210))
    return pygame.transform.smoothscale(img, (WIDTH, HEIGHT))


def _as_color(value: ColorValue) -> pygame.Color:
    if isinstance(value, pygame.Color):
        return value
    return pygame.Color(*value)


def _rounded_rect(
    surface: pygame.Surface,
    rect: pygame.Rect,
    color: ColorValue,
    radius: int = 16,
    width: int = 0,
) -> None:
    pygame.draw.rect(surface, _as_color(color), rect, width=width, border_radius=radius)


class StartMenu:
    def __init__(self, localizer: Localizer | None = None) -> None:
        self.localizer = localizer or Localizer()
        self.bg = _load_image(MENU_BG_PATH)

        self.font_title = load_font(int(FONT_SIZE * 2.4))
        self.font_btn = load_font(int(FONT_SIZE * 1.4))
        self.font_hint = load_font(int(FONT_SIZE * 1.1))

        self.items: list[MenuItem] = []
        self.selected: int = 0

        self.btn_w: int = int(WIDTH * BTN_WIDTH_RATIO)
        self.btn_h: int = BTN_HEIGHT
        self.btn_gap: int = BTN_GAP
        self.btn_rects: list[pygame.Rect] = []
        self.set_items(MAIN_MENU_ITEMS)

        self.controls_open: bool = False
        self.controls_lines: list[str | LocalizedText] = ["—"]

    def set_items(self, items: Sequence[MenuItem]) -> None:
        self.items = list(items)
        self.btn_rects = self._build_button_rects()

    def set_controls(self, text: str | Sequence[str | LocalizedText]) -> None:
        self.controls_lines.clear()
        if isinstance(text, str):
            self.controls_lines.extend(text.splitlines())
        else:
            self.controls_lines.extend(text)

    def open_controls(self) -> None:
        self.controls_open = True

    def _build_button_rects(self) -> list[pygame.Rect]:
        cx = WIDTH // 2
        total_h = len(self.items) * self.btn_h + (len(self.items) - 1) * self.btn_gap
        top = HEIGHT // 2 - total_h // 2 + 20
        rects: list[pygame.Rect] = []
        y = top
        for _ in self.items:
            r = pygame.Rect(0, 0, self.btn_w, self.btn_h)
            r.centerx = cx
            r.y = y
            rects.append(r)
            y += self.btn_h + self.btn_gap
        return rects

    def _draw_title(self, surface: pygame.Surface) -> None:
        t_shadow = self.font_title.render(TITLE_TEXT, True, (255, 180, 200))
        t_fill = self.font_title.render(TITLE_TEXT, True, (255, 255, 255))
        x = WIDTH // 2 - t_fill.get_width() // 2
        surface.blit(t_shadow, (x + 3, TITLE_Y + 3))
        surface.blit(t_fill, (x, TITLE_Y))

    def _draw_button(
        self, surface: pygame.Surface, rect: pygame.Rect, label: str, selected: bool
    ) -> None:

        _rounded_rect(surface, rect.move(0, 6), pygame.Color(0, 0, 0, 80), 18)

        base_top = (255, 210, 200)
        base_bottom = (255, 160, 180)
        border = (220, 120, 140)

        _rounded_rect(surface, rect.inflate(12, 8), border, 20)

        top = pygame.Rect(rect.x + 4, rect.y + 4, rect.width - 8, rect.height // 2 - 2)
        bottom = pygame.Rect(
            rect.x + 4, rect.y + rect.height // 2, rect.width - 8, rect.height // 2 - 2
        )
        _rounded_rect(surface, top, base_top, 16)
        _rounded_rect(surface, bottom, base_bottom, 16)

        if selected:
            glow = rect.inflate(18, 14)
            pygame.draw.rect(surface, (255, 240, 250), glow, 5, border_radius=20)

        txt = self.font_btn.render(label, True, (120, 40, 60))
        surface.blit(
            txt,
            (rect.centerx - txt.get_width() // 2, rect.centery - txt.get_height() // 2),
        )

    def _draw_hints(self, surface: pygame.Surface) -> None:
        hint = self.localizer.text("menu.hint")
        s1 = self.font_hint.render(hint, True, (100, 70, 80))
        s2 = self.font_hint.render(hint, True, (255, 235, 240))
        x = WIDTH // 2 - s2.get_width() // 2
        y = HEIGHT - s2.get_height() - 18
        surface.blit(s1, (x + 2, y + 2))
        surface.blit(s2, (x, y))

    def _draw_controls_modal(self, surface: pygame.Surface) -> None:
        dim = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 100))
        surface.blit(dim, (0, 0))

        card_w = int(WIDTH * 0.74)
        card_h = int(HEIGHT * 0.66)
        card = pygame.Rect(0, 0, card_w, card_h)
        card.center = (WIDTH // 2, HEIGHT // 2)

        _rounded_rect(surface, card.inflate(16, 16), pygame.Color(255, 190, 210), 22)
        _rounded_rect(surface, card, pygame.Color(255, 240, 245), 18)
        pygame.draw.rect(surface, (255, 170, 190), card, 4, border_radius=18)

        title = self.font_title.render(
            self.localizer.text("controls.title"), True, (180, 60, 90)
        )
        surface.blit(title, (card.centerx - title.get_width() // 2, card.y + 18))

        lines = self.controls_lines or ["—"]
        y = card.y + 86
        x_pad = card.x + 28
        for line in lines:
            resolved_line = (
                self.localizer.resolve(line)
                if isinstance(line, LocalizedText)
                else line
            )
            text_surf = self.font_hint.render(resolved_line, True, (150, 40, 70))
            surface.blit(text_surf, (x_pad, y))
            y += int(self.font_hint.get_height() * 1.35)

        footer = self.font_hint.render(
            self.localizer.text("controls.close"), True, (90, 60, 80)
        )
        surface.blit(
            footer,
            (
                card.centerx - footer.get_width() // 2,
                card.bottom - footer.get_height() - 16,
            ),
        )

    def handle_event(self, e: pygame.event.Event) -> MenuAction | None:
        if self.controls_open:
            if e.type == pygame.KEYDOWN and e.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                self.controls_open = False
            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                self.controls_open = False
            return None

        if e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_UP, pygame.K_w):
                self.selected = (self.selected - 1) % len(self.items)
            elif e.key in (pygame.K_DOWN, pygame.K_s):
                self.selected = (self.selected + 1) % len(self.items)
            elif e.key == pygame.K_RETURN:
                return self.items[self.selected].action
            elif e.key == pygame.K_ESCAPE:
                return MenuAction.QUIT

        elif e.type == pygame.MOUSEMOTION:
            mx, my = e.pos
            for i, r in enumerate(self.btn_rects):
                if r.collidepoint(mx, my):
                    self.selected = i
                    break

        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            mx, my = e.pos
            for i, r in enumerate(self.btn_rects):
                if r.collidepoint(mx, my):
                    self.selected = i
                    return self.items[i].action

        return None

    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(self.bg, (0, 0))

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((255, 230, 240, 50))
        surface.blit(overlay, (0, 0))

        self._draw_title(surface)

        for i, (item, rect) in enumerate(zip(self.items, self.btn_rects, strict=True)):
            self._draw_button(
                surface,
                rect,
                self.localizer.text(item.label_key),
                selected=(i == self.selected),
            )

        self._draw_hints(surface)

        if self.controls_open:
            self._draw_controls_modal(surface)
