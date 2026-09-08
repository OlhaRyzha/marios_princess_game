import math
import random
from typing import cast

import pygame

from game.data.blocks import (
    CAVES_BLOCKS,
    MEADOWS_BLOCKS,
    WOODS_BLOCKS,
)
from game.data.locations import (
    CAVES_PATTERN,
    MEADOWS_PATTERN,
    WOODS_PATTERN,
    LocationName,
    crawl_gap,
)
from game.levels.obstacle import Anchor, Obstacle
from game.utils.constants import LEVEL_WIDTH, OBSTACLE_SCALE


class MovingObstacle(Obstacle):

    def __init__(
        self,
        *args,
        amplitude: float = 80.0,
        speed: float = 1.2,
        phase: float = 0.0,
        move_axis: str = "y",
        bounds: tuple[int, int] | None = None,
        origin: str = "center",
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self._base_pos = pygame.Vector2(self.rect.topleft)
        self._theta = float(phase) % (
            math.tau if hasattr(math, "tau") else 2.0 * math.pi
        )
        self._amplitude = abs(float(amplitude))
        self._omega = 2.0 * math.pi * max(0.0, float(speed))
        self._axis = move_axis
        self._bounds = bounds
        self._origin = origin
        self._base_bottom = float(self.rect.bottom)
        self._base_top = float(self.rect.top)

    def _advance_phase(self, dt: float) -> float:
        if self._omega == 0.0:
            return math.sin(self._theta)
        self._theta = (self._theta + self._omega * float(dt)) % (
            math.tau if hasattr(math, "tau") else 2.0 * math.pi
        )
        return math.sin(self._theta)

    def update(self, dt: float, *_):
        wave = self._advance_phase(dt)
        if self._axis == "y":
            if self._origin == "bottom":
                normalized = 0.5 * (wave + 1.0)
                new_bottom = self._base_bottom - normalized * self._amplitude
                self.rect.bottom = int(new_bottom)
            elif self._origin == "top":
                normalized = 0.5 * (wave + 1.0)
                new_top = self._base_top + normalized * self._amplitude
                self.rect.top = int(new_top)
            else:
                self.rect.y = int(self._base_pos.y + self._amplitude * wave)
        elif self._axis == "x":
            x = self._base_pos.x + self._amplitude * wave
            if self._bounds:
                left, right = self._bounds
                x = max(left, min(x, right - self.rect.width))
            self.rect.x = int(x)
        elif self._axis == "xy":
            self.rect.y = int(self._base_pos.y + self._amplitude * wave)
            x = self._base_pos.x + self._amplitude * wave
            if self._bounds:
                left, right = self._bounds
                x = max(left, min(x, right - self.rect.width))
            self.rect.x = int(x)


def _rand_from_range(value: object, *, default: float, rng: random.Random) -> float:
    if value is None:
        return float(default)
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, tuple) and len(value) == 2:
        lo, hi = value
        lo_f = float(lo)
        hi_f = float(hi)
        if lo_f == hi_f:
            return lo_f
        low, high = (lo_f, hi_f) if lo_f < hi_f else (hi_f, lo_f)
        return rng.uniform(low, high)
    return float(default)


MOVING_BLOCK_BEHAVIOUR: dict[str, dict[str, float | tuple[float, float] | str]] = {
    "ice_tile": {
        "origin": "bottom",
        "travel": (180.0, 220.0),
        "speed": (0.16, 0.26),
    },
    "one_way_platform": {
        "origin": "center",
        "amplitude": (70.0, 110.0),
        "speed": (0.28, 0.44),
    },
    "wooden_platform_moving": {
        "origin": "bottom",
        "travel": (160.0, 210.0),
        "speed": (0.14, 0.24),
    },
}


def _blocks_for_location(location: LocationName):
    if location == "sunny_meadows":
        return MEADOWS_BLOCKS, MEADOWS_PATTERN
    if location == "mushroom_woods":
        return WOODS_BLOCKS, WOODS_PATTERN
    return CAVES_BLOCKS, CAVES_PATTERN


def _resolve_anchor(anchor_name: str, air_offset: int | str) -> tuple[Anchor, int]:
    if anchor_name != "air":
        return "ground", 0
    offset = crawl_gap() if air_offset == "crawl" else int(air_offset)
    return "air", offset


def _movement_parameters(
    config: dict[str, float | tuple[float, float] | str], rng: random.Random
) -> tuple[str, float, float, float]:
    origin = str(config.get("origin", "center"))
    travel_default = 190.0 if origin in ("bottom", "top") else 90.0
    travel = _rand_from_range(config.get("travel"), default=travel_default, rng=rng)
    amplitude = (
        travel
        if origin in ("bottom", "top")
        else _rand_from_range(config.get("amplitude"), default=travel, rng=rng)
    )
    speed = _rand_from_range(config.get("speed"), default=1.0, rng=rng)
    phase_config = config.get("phase")
    if phase_config is not None:
        phase = _rand_from_range(phase_config, default=0.0, rng=rng)
    elif origin == "bottom":
        phase = -math.pi * 0.5
    elif origin == "top":
        phase = math.pi * 0.5
    else:
        phase = rng.uniform(0.0, math.tau)
    return origin, amplitude, speed, phase


def _build_obstacle(
    *,
    key: str,
    image_def: str,
    x: int,
    anchor: Anchor,
    air_offset: int,
    scale: float,
    rng: random.Random,
) -> Obstacle:
    movement = MOVING_BLOCK_BEHAVIOUR.get(key.lower())
    if movement is None:
        return Obstacle(
            image_def=image_def,
            pos=(x, 0),
            scale=scale,
            anchor=anchor,
            air_bottom_offset=air_offset,
        )
    origin, amplitude, speed, phase = _movement_parameters(movement, rng)
    return cast(
        Obstacle,
        MovingObstacle(
            image_def=image_def,
            pos=(x, 0),
            scale=scale,
            anchor=anchor,
            air_bottom_offset=air_offset,
            amplitude=amplitude,
            speed=speed,
            phase=phase,
            move_axis="y",
            origin=origin,
        ),
    )


def build_obstacles(
    *,
    location: LocationName,
    start_x: int,
    repeats: int = 10,
    safe_gap: int = 520,
    step_x: int = 320,
    scale: float = OBSTACLE_SCALE,
    rng: random.Random,
) -> tuple[list[Obstacle], int]:
    obstacles: list[Obstacle] = []
    blocks, pattern = _blocks_for_location(location)

    x = start_x + safe_gap
    max_right = x

    for _ in range(repeats):
        for key, anchor_name, air_offset in pattern:
            if key not in blocks:
                continue
            anchor, resolved_offset = _resolve_anchor(anchor_name, air_offset)
            obstacle = _build_obstacle(
                key=key,
                image_def=blocks[key],
                x=x,
                anchor=anchor,
                air_offset=resolved_offset,
                scale=scale,
                rng=rng,
            )
            obstacles.append(obstacle)
            x += step_x
            max_right = max(max_right, obstacle.rect.right)

    return obstacles, max_right


def boss_gate_position(max_right: int, *, margin: int = 140) -> int:
    return min(max_right + margin, LEVEL_WIDTH - 100)
