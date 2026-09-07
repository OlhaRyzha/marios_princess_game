from typing import Protocol

import pygame


class TimeSource(Protocol):
    def now_ms(self) -> int: ...


class PygameTimeSource:
    def now_ms(self) -> int:
        return pygame.time.get_ticks()
