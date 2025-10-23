from __future__ import annotations

import pygame

from game.utils import FONT_SIZE, WIDTH
from game.utils.fonts import load_font

HUD_BAR_WIDTH = 220
HUD_BAR_HEIGHT = 16
HUD_PADDING = 16


class HealthHUD:
    def __init__(self):
        self.font = load_font(FONT_SIZE)

    def draw(
        self,
        surface: pygame.Surface,
        health: int,
        max_health: int,
        *,
        collectibles: tuple[int, int] | None = None,
        icon: pygame.Surface | None = None,
    ):
        x = WIDTH - HUD_PADDING - HUD_BAR_WIDTH
        y = HUD_PADDING

        outline = pygame.Rect(x, y, HUD_BAR_WIDTH, HUD_BAR_HEIGHT)
        pygame.draw.rect(surface, (30, 30, 30), outline, border_radius=6)
        pygame.draw.rect(surface, (220, 220, 220), outline, width=2, border_radius=6)

        ratio = 0.0 if max_health <= 0 else max(0.0, min(1.0, health / max_health))
        fill_w = int((HUD_BAR_WIDTH - 4) * ratio)
        fill_rect = pygame.Rect(x + 2, y + 2, fill_w, HUD_BAR_HEIGHT - 4)
        color = (int(255 * (1 - ratio)), int(200 * ratio + 55 * (1 - ratio)), 80)
        pygame.draw.rect(surface, color, fill_rect, border_radius=5)

        label = self.font.render(f"HP: {health}/{max_health}", True, (240, 240, 240))
        surface.blit(
            label, (x + HUD_BAR_WIDTH - label.get_width(), y + HUD_BAR_HEIGHT + 6)
        )

        if collectibles and icon and collectibles[1] > 0:
            collected, goal = collectibles
            progress_text = f"{collected}/{goal}"
            text_surf = self.font.render(progress_text, True, (240, 240, 240))

            margin = 18
            total_width = icon.get_width() + 8 + text_surf.get_width()
            base_x = max(HUD_PADDING, x - margin - total_width)
            icon_rect = icon.get_rect()
            icon_rect.centery = y + HUD_BAR_HEIGHT // 2
            icon_rect.left = base_x
            surface.blit(icon, icon_rect)

            text_pos = (
                icon_rect.right + 8,
                y + HUD_BAR_HEIGHT // 2 - text_surf.get_height() // 2,
            )
            surface.blit(text_surf, text_pos)
