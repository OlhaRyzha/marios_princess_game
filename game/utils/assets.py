from __future__ import annotations

import os
from typing import List

import pygame

from game.utils import SPRITES_DIR, TARGET_H, load_image, scale_to_height


def load_sequence(
    folder: str, prefix: str, target_h: int | None = TARGET_H
) -> List[pygame.Surface]:
    path = os.path.join(SPRITES_DIR, folder)
    if not os.path.isdir(path):
        return []
    names = sorted(
        n for n in os.listdir(path) if n.startswith(prefix) and n.endswith(".png")
    )
    frames: List[pygame.Surface] = []
    for n in names:
        img = load_image(os.path.join(path, n))
        if target_h:
            img = scale_to_height(img, target_h)
        frames.append(img)
    return frames
