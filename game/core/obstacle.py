import os
from typing import Literal

import pygame

from game.utils.constants import GROUND_Y

Anchor = Literal["ground", "air"]


def _to_surface(src: str) -> pygame.Surface:
    if isinstance(src, pygame.Surface):
        return src
    if isinstance(src, str):
        if not os.path.exists(src):
            raise FileNotFoundError(f"Obstacle image not found: {src}")
        return pygame.image.load(src).convert_alpha()
    if isinstance(src, dict):
        img = src.get("image") or src.get("path") or src.get("image_path")
        if isinstance(img, pygame.Surface):
            return img
        if isinstance(img, str):
            if not os.path.exists(img):
                raise FileNotFoundError(f"Obstacle image not found: {img}")
            return pygame.image.load(img).convert_alpha()
        size = src.get("size")
        if size:
            surf = pygame.Surface(size, pygame.SRCALPHA)
            surf.fill((170, 170, 200, 220))
            return surf
    surf = pygame.Surface((48, 32), pygame.SRCALPHA)
    surf.fill((200, 120, 120, 230))
    return surf


class Obstacle(pygame.sprite.Sprite):

    def __init__(
        self,
        image_def: str,
        pos: tuple[int, int],
        *,
        scale: float = 1.0,
        anchor: Anchor = "ground",
        hazard: bool = False,
        air_bottom_offset: int = 140,
    ):
        super().__init__()
        base: pygame.Surface = _to_surface(image_def)
        if scale != 1.0:
            w, h = base.get_size()
            self.image: pygame.Surface = pygame.transform.smoothscale(
                base, (max(1, int(w * scale)), max(1, int(h * scale)))
            )
        else:
            self.image = base.copy()

        self.rect: pygame.Rect = self.image.get_rect(topleft=pos)
        if anchor == "ground":
            self.rect.bottom = GROUND_Y
        else:
            self.rect.bottom = GROUND_Y - air_bottom_offset

        self.mask: pygame.mask.Mask = pygame.mask.from_surface(self.image)
        self.hazard = hazard
        self.anchor = anchor
