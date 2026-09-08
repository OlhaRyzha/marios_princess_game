from dataclasses import dataclass


@dataclass(slots=True)
class LevelCamera:
    """Keep the horizontal viewport inside level boundaries."""

    viewport_width: int
    level_width: int
    x: float = 0.0

    def follow(self, target_x: float) -> None:
        desired_x = target_x - self.viewport_width * 0.5
        self.x = max(0.0, min(desired_x, self.level_width - self.viewport_width))

    def reset(self) -> None:
        self.x = 0.0
