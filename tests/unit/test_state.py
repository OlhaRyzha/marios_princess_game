from game.data.locations import LOCATION_ORDER
from game.state import GameMode, GameState, Progress


def test_new_progress_starts_at_first_location() -> None:
    progress = Progress()

    assert progress.unlocked == {LOCATION_ORDER[0]}
    assert progress.completed == set()
    assert progress.pending_location == LOCATION_ORDER[0]


def test_progress_reset_starts_a_new_playthrough() -> None:
    progress = Progress(
        unlocked=set(LOCATION_ORDER),
        completed=set(LOCATION_ORDER),
        pending_location=LOCATION_ORDER[-1],
    )

    progress.reset()

    assert progress.unlocked == {LOCATION_ORDER[0]}
    assert progress.completed == set()
    assert progress.pending_location == LOCATION_ORDER[0]


def test_complete_unlocks_and_selects_next_location() -> None:
    progress = Progress()

    completed_now = progress.complete("sunny_meadows")

    assert completed_now
    assert progress.completed == {"sunny_meadows"}
    assert progress.unlocked == {"sunny_meadows", "mushroom_woods"}
    assert progress.pending_location == "mushroom_woods"


def test_complete_is_idempotent() -> None:
    progress = Progress()
    progress.complete("sunny_meadows")

    completed_again = progress.complete("sunny_meadows")

    assert not completed_again
    assert progress.completed == {"sunny_meadows"}
    assert progress.unlocked == {"sunny_meadows", "mushroom_woods"}


def test_select_rejects_locked_location() -> None:
    progress = Progress()

    selected = progress.select("crystal_caves")

    assert not selected
    assert progress.pending_location == "sunny_meadows"


def test_game_state_uses_typed_defaults() -> None:
    state = GameState[object]()

    assert state.mode is GameMode.MENU
    assert state.running
    assert state.scene is None
    assert state.progress.pending_location == "sunny_meadows"
