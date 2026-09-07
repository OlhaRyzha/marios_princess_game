from typing import Protocol

import pygame


class CollisionSprite(Protocol):
    rect: pygame.Rect


def collide_mask(a: CollisionSprite, b: CollisionSprite) -> bool:
    mask_a = getattr(a, "mask", None)
    mask_b = getattr(b, "mask", None)
    if mask_a is not None and mask_b is not None:
        offset = (b.rect.x - a.rect.x, b.rect.y - a.rect.y)
        return mask_a.overlap(mask_b, offset) is not None
    return a.rect.colliderect(b.rect)
