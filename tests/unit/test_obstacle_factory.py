from game.core.obstacle_factory import boss_gate_position
from game.utils.constants import LEVEL_WIDTH


def test_boss_gate_is_placed_after_last_obstacle() -> None:
    assert boss_gate_position(1_000, margin=140) == 1_140


def test_boss_gate_stays_inside_level() -> None:
    assert boss_gate_position(LEVEL_WIDTH, margin=140) == LEVEL_WIDTH - 100
