from collections.abc import Iterable

import pygame


class Animation:
    def __init__(
        self,
        frames: "Iterable[pygame.Surface] | None",
        fps: int = 10,
        loop: bool = True,
    ):
        frame_list = list(frames) if frames is not None else []
        if not frame_list:
            frame_list = [pygame.Surface((64, 64), pygame.SRCALPHA)]
        self.frames: list[pygame.Surface] = frame_list
        self.loop = loop
        self.fps = fps
        self.time = 0.0

    def reset(self) -> None:
        self.time = 0.0

    def update(self, dt: float) -> None:
        self.time += dt

    def image(self) -> "pygame.Surface":
        idx = int(self.time * self.fps)
        if self.loop:
            idx %= len(self.frames)
        else:
            idx = min(idx, len(self.frames) - 1)
        return self.frames[idx]
