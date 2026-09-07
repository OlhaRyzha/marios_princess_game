import math
import random
from functools import cache

import pygame

from game.utils.images import scale_to_height


def _star_points(radius: float, spikes: int = 5) -> list[tuple[float, float]]:
    pts: list[tuple[float, float]] = []
    outer_r = radius
    inner_r = radius * 0.45
    angle = math.pi / spikes
    for i in range(spikes * 2):
        r = outer_r if i % 2 == 0 else inner_r
        theta = i * angle - math.pi / 2
        pts.append((math.cos(theta) * r, math.sin(theta) * r))
    return pts


def _render_shape(kind: str, size: int) -> pygame.Surface:
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    center = (size / 2, size / 2)

    if kind == "royal_badge":
        pts = _star_points(size * 0.42)
        points = [(center[0] + x, center[1] + y) for x, y in pts]
        pygame.draw.polygon(surf, (250, 206, 70), points)
        pygame.draw.polygon(surf, (255, 235, 140), points, width=3)
        halo = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(
            halo, (255, 245, 190, 120), (size // 2, size // 2), size // 2
        )
        surf.blit(halo, (0, 0), special_flags=pygame.BLEND_PREMULTIPLIED)
    elif kind == "forest_fruit":
        body_color = (220, 70, 110)
        pygame.draw.circle(surf, body_color, (size // 2, size // 2), size // 2 - 2)
        pygame.draw.circle(
            surf, (255, 160, 180), (int(size * 0.38), int(size * 0.32)), size // 5
        )
        leaf = [
            (size * 0.42, size * 0.28),
            (size * 0.60, size * 0.12),
            (size * 0.74, size * 0.30),
        ]
        pygame.draw.polygon(surf, (60, 170, 90), leaf)
    elif kind == "crystal_flake":
        center_pt = (size // 2, size // 2)
        color = (140, 200, 255)
        pygame.draw.circle(surf, (200, 235, 255), center_pt, size // 5)
        for angle in range(0, 360, 45):
            length = size // 2 - 4
            dx = length * math.cos(math.radians(angle))
            dy = length * math.sin(math.radians(angle))
            end = (center_pt[0] + dx, center_pt[1] + dy)
            pygame.draw.line(surf, color, center_pt, end, width=3)
            branch = (
                (end[0] - dx * 0.2 - dy * 0.15, end[1] - dy * 0.2 + dx * 0.15),
                end,
                (end[0] - dx * 0.2 + dy * 0.15, end[1] - dy * 0.2 - dx * 0.15),
            )
            pygame.draw.lines(surf, color, False, branch, width=2)
    else:
        pygame.draw.circle(surf, (255, 235, 150), (size // 2, size // 2), size // 2)
        pygame.draw.circle(
            surf, (255, 255, 255, 180), (size // 2 - 4, size // 2 - 6), size // 4
        )
    return surf


@cache
def collectible_surface(kind: str, size: int) -> pygame.Surface:
    return _render_shape(kind, size)


class Collectible(pygame.sprite.Sprite):
    def __init__(
        self,
        kind: str,
        pos: tuple[int, int],
        *,
        rng: random.Random,
        size: int = 46,
        surface: pygame.Surface | None = None,
    ):
        super().__init__()
        self.kind = kind
        self._base_y = float(pos[1])
        self._phase = rng.uniform(0.0, math.tau)
        self._bob_range = 6.0
        self._bob_speed = 2.4
        if surface is not None:
            self.image: pygame.Surface = surface.copy()
        else:
            self.image = collectible_surface(kind, size).copy()
        self.rect: pygame.Rect = self.image.get_rect(center=pos)

    def update(self, dt: float):
        self._phase = (self._phase + self._bob_speed * dt) % math.tau
        offset = math.sin(self._phase) * self._bob_range
        self.rect.centery = int(self._base_y + offset)

    @staticmethod
    def icon(
        kind: str,
        size: int = 28,
        surface: pygame.Surface | None = None,
    ) -> pygame.Surface:
        if surface is not None:
            return scale_to_height(surface, size)
        return collectible_surface(kind, size).copy()
