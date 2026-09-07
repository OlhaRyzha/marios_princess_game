from collections.abc import Sequence

import pygame

from game.utils.constants import FONT_SIZE
from game.utils.fonts import load_font
from game.utils.paths import resolve_project_path


class FinaleCinematic:

    def __init__(
        self,
        *,
        duration_ms: int = 4200,
        font_size: int = FONT_SIZE,
        hug_candidates: Sequence[str] | None = None,
    ):
        self.duration_ms = duration_ms
        self._start_ms: int | None = None
        self._hug_img: pygame.Surface | None = None
        self._hug_candidates = tuple(
            hug_candidates
            or (
                "assets/hug/hug.png",
                "assets/sprites/finale/hug/hug.png",
                "assets/sprites/hug/hug.png",
            )
        )
        self._font_big = load_font(int(font_size * 3.2))
        self._font_small = load_font(int(font_size * 1.4))

    def reset(self) -> None:
        self._start_ms = None

    def start(self, now_ms: int) -> None:
        self._start_ms = now_ms

    def is_running(self) -> bool:
        return self._start_ms is not None

    def ready_for_modal(self, now_ms: int) -> bool:
        if self._start_ms is None:
            return False
        return now_ms - self._start_ms >= self.duration_ms

    def ensure_assets(self) -> None:
        if self._hug_img is not None:
            return
        for candidate in self._hug_candidates:
            path = resolve_project_path(candidate)
            if path.is_file():
                try:
                    self._hug_img = pygame.image.load(path).convert_alpha()
                    return
                except (OSError, pygame.error):
                    continue
        if self._hug_img is None:
            self._hug_img = pygame.Surface((256, 256), pygame.SRCALPHA)

    def draw(self, surface: pygame.Surface) -> None:
        self.ensure_assets()

        w, h = surface.get_size()
        rings = [
            (242, 118, 34),
            (233, 103, 30),
            (224, 90, 26),
            (211, 78, 23),
            (197, 66, 20),
            (183, 58, 18),
        ]
        cx, cy = w // 2, h // 2
        max_r = int(min(w, h) * 0.95 // 2)
        step = max_r // (len(rings) + 1)

        surface.fill(rings[0])
        r = max_r
        for color in rings[1:]:
            pygame.draw.circle(surface, color, (cx, cy), r)
            r -= step

        shadow = (120, 60, 20)
        fg = (255, 216, 120)

        the_text = self._font_small.render("THE", True, fg)
        the_shadow = self._font_small.render("THE", True, shadow)
        the_pos = (cx - the_text.get_width() // 2, cy - int(h * 0.34))
        surface.blit(the_shadow, (the_pos[0] + 4, the_pos[1] + 4))
        surface.blit(the_text, the_pos)

        end_text = self._font_big.render("END", True, fg)
        end_shadow = self._font_big.render("END", True, shadow)
        end_pos = (cx - end_text.get_width() // 2, cy - int(h * 0.27))
        surface.blit(end_shadow, (end_pos[0] + 6, end_pos[1] + 6))
        surface.blit(end_text, end_pos)

        if self._hug_img is not None:
            img = self._hug_img
            target_h = int(h * 0.55)
            scale = target_h / img.get_height()
            target_w = int(img.get_width() * scale)
            hug_scaled = pygame.transform.smoothscale(img, (target_w, target_h))
            surface.blit(
                hug_scaled,
                (cx - target_w // 2, cy - target_h // 2 + int(h * 0.10)),
            )
