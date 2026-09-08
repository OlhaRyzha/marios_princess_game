import random

from game.levels.obstacle_factory import boss_gate_position, build_obstacles
from game.utils.constants import LEVEL_WIDTH


def test_boss_gate_is_placed_after_last_obstacle() -> None:
    assert boss_gate_position(1_000, margin=140) == 1_140


def test_boss_gate_stays_inside_level() -> None:
    assert boss_gate_position(LEVEL_WIDTH, margin=140) == LEVEL_WIDTH - 100


def test_obstacle_generation_is_repeatable_with_the_same_seed(
    pygame_runtime: None,
) -> None:
    first, _ = build_obstacles(
        location="mushroom_woods",
        start_x=240,
        repeats=2,
        rng=random.Random(2026),
    )
    second, _ = build_obstacles(
        location="mushroom_woods",
        start_x=240,
        repeats=2,
        rng=random.Random(2026),
    )

    for obstacle in first:
        obstacle.update(0.25)
    for obstacle in second:
        obstacle.update(0.25)

    assert [obstacle.rect.copy() for obstacle in first] == [
        obstacle.rect.copy() for obstacle in second
    ]
