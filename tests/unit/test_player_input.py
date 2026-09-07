import pytest

from game.core.player import Princess
from game.systems.input_state import InputState
from game.utils.constants import GRAVITY, GROUND_Y, JUMP_V, SPEED_RUN, SPEED_WALK
from tests.factories.time import FakeTimeSource


@pytest.fixture
def princess(pygame_runtime: None) -> Princess:
    player = Princess((240, GROUND_Y), time_source=FakeTimeSource())
    player.on_ground = True
    return player


@pytest.mark.parametrize(
    ("input_state", "expected_velocity"),
    [
        (InputState(right=True), SPEED_WALK),
        (InputState(right=True, run=True), SPEED_RUN),
        (InputState(left=True), -SPEED_WALK),
    ],
)
def test_direction_and_run_speed_come_from_input_state(
    princess: Princess,
    input_state: InputState,
    expected_velocity: float,
) -> None:
    princess.update(1 / 60, input_state)

    assert princess.vel.x == expected_velocity


def test_jump_comes_from_input_state(princess: Princess) -> None:
    princess.update(1 / 60, InputState(jump=True))

    assert princess.vel.y == JUMP_V + GRAVITY
    assert not princess.on_ground
