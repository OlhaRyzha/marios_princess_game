from game.ui.world_map_state import WorldMapState


def test_map_state_owns_navigation_and_progress() -> None:
    state = WorldMapState(["sunny_meadows", "mushroom_woods", "crystal_caves"])

    assert state.selected_location == "sunny_meadows"
    assert state.mario_location == "sunny_meadows"

    state.set_progress(
        unlocked={"sunny_meadows", "mushroom_woods"},
        completed={"sunny_meadows"},
    )
    state.move(1)

    assert state.selected_location == "mushroom_woods"
    assert state.mario_location == "sunny_meadows"
