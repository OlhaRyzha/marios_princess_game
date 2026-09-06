from dataclasses import dataclass

import pygame
from pygame.mask import Mask


@dataclass(slots=True)
class MaskedSpriteDouble:
    """Small test double that satisfies the collision protocol."""

    rect: pygame.Rect
    mask: Mask


def make_masked_sprite(
    *,
    size: tuple[int, int] = (10, 10),
    topleft: tuple[int, int] = (0, 0),
    opaque: bool = True,
) -> MaskedSpriteDouble:
    """Build a sprite double with explicit geometry and mask contents."""
    surface = pygame.Surface(size, pygame.SRCALPHA)
    if opaque:
        surface.fill("white")
    return MaskedSpriteDouble(
        rect=surface.get_rect(topleft=topleft),
        mask=pygame.mask.from_surface(surface),
    )
