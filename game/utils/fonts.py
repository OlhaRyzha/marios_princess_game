from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

import pygame

from game.utils import FONT_NAME, BACKGROUNDS_DIR


@lru_cache(maxsize=1)
def _resolve_font_path() -> str | None:
    try:

        if FONT_NAME and os.path.exists(FONT_NAME):
            return FONT_NAME

        assets_dir = Path(BACKGROUNDS_DIR).resolve().parent
        bundled = assets_dir / "fonts" / "DejaVuSans.ttf"
        if bundled.exists():
            return str(bundled)

        candidates: tuple[str, ...] = (
            *([FONT_NAME] if FONT_NAME else []),
            "Arial Unicode MS",
            "arialunicode",
            "DejaVu Sans",
            "DejaVuSans",
            "Noto Sans",
        )
        for name in candidates:
            if not name:
                continue
            path = pygame.font.match_font(name)
            if path and os.path.exists(path):
                return path
    except Exception:
        pass
    return None


def load_font(size: int, *, bold: bool = False) -> pygame.font.Font:
    path = _resolve_font_path()
    if path:
        return pygame.font.Font(path, size)

    family = FONT_NAME or pygame.font.get_default_font()
    return pygame.font.SysFont(family, size, bold=bold)
