import pygame

from game.utils.constants import SPRITES_DIR, TARGET_H
from game.utils.images import load_image, scale_to_height


def load_sequence(
    folder: str, prefix: str, target_h: int | None = TARGET_H
) -> "list[pygame.Surface]":
    path = SPRITES_DIR / folder
    if not path.is_dir():
        return []
    names = sorted(
        item.name
        for item in path.iterdir()
        if item.name.startswith(prefix) and item.suffix == ".png"
    )
    frames: list[pygame.Surface] = []
    for n in names:
        img = load_image(path / n)
        if target_h:
            img = scale_to_height(img, target_h)
        frames.append(img)
    return frames
