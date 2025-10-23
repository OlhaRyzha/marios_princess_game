from __future__ import annotations

import pygame
from pygame.mask import Mask
from typing import Protocol


class MaskedSprite(Protocol):
    rect: pygame.Rect
    mask: Mask


def collide_mask(a: MaskedSprite, b: MaskedSprite) -> bool:
    mask_a = getattr(a, "mask", None)
    mask_b = getattr(b, "mask", None)
    if mask_a is not None and mask_b is not None:
        offset = (b.rect.x - a.rect.x, b.rect.y - a.rect.y)
        return mask_a.overlap(mask_b, offset) is not None
    return a.rect.colliderect(b.rect)


__all__ = ["MaskedSprite", "collide_mask"]
