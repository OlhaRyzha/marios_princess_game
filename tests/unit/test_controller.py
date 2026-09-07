import pytest

from game.actions import MapAction, MapEvent, MenuAction
from game.controller import ControllerEffect, GameController
from game.state import GameMode, GameState


@pytest.mark.parametrize(
    ("current_mode", "expected_mode"),
    [
        (GameMode.GAME, GameMode.MENU_PAUSE),
        (GameMode.MENU_PAUSE, GameMode.GAME),
        (GameMode.MAP, GameMode.MENU),
        (GameMode.MAP_OVERLAY, GameMode.GAME),
    ],
)
def test_escape_changes_supported_mode(
    current_mode: GameMode, expected_mode: GameMode
) -> None:
    state = GameState[object](mode=current_mode)
    controller = GameController(state)

    handled = controller.handle_escape()

    assert handled
    assert state.mode is expected_mode


def test_escape_leaves_main_menu_for_menu_handler() -> None:
    state = GameState[object]()
    controller = GameController(state)

    handled = controller.handle_escape()

    assert not handled
    assert state.mode is GameMode.MENU


def test_map_toggle_requires_an_active_scene() -> None:
    state = GameState[object](mode=GameMode.GAME)
    controller = GameController(state)

    assert not controller.toggle_map()
    assert state.mode is GameMode.GAME

    state.scene = object()

    assert controller.toggle_map()
    assert state.mode is GameMode.MAP_OVERLAY
    assert controller.toggle_map()
    assert state.mode is GameMode.GAME


@pytest.mark.parametrize(
    ("current_mode", "expected_mode"),
    [
        (GameMode.MENU, GameMode.MAP),
        (GameMode.MENU_PAUSE, GameMode.MAP_OVERLAY),
    ],
)
def test_open_map_uses_context(current_mode: GameMode, expected_mode: GameMode) -> None:
    state = GameState[object](mode=current_mode)
    controller = GameController(state)

    effect = controller.handle_menu(MenuAction.OPEN_MAP)

    assert effect is None
    assert state.mode is expected_mode


def test_start_game_requests_scene_creation() -> None:
    state = GameState[object]()
    controller = GameController(state)

    effect = controller.handle_menu(MenuAction.START_GAME)

    assert effect is ControllerEffect.START_SCENE
    assert state.mode is GameMode.GAME


def test_controls_and_quit_are_explicit() -> None:
    state = GameState[object]()
    controller = GameController(state)

    effect = controller.handle_menu(MenuAction.OPEN_CONTROLS)

    assert effect is ControllerEffect.OPEN_CONTROLS
    assert state.running

    controller.handle_menu(MenuAction.QUIT)

    assert not state.running


def test_map_starts_only_unlocked_location() -> None:
    state = GameState[object](mode=GameMode.MAP)
    controller = GameController(state)

    locked_effect = controller.handle_map(MapEvent(MapAction.START, "crystal_caves"))

    assert locked_effect is None
    assert state.mode is GameMode.MAP

    start_effect = controller.handle_map(MapEvent(MapAction.START, "sunny_meadows"))

    assert start_effect is ControllerEffect.START_SCENE
    assert state.mode is GameMode.GAME
    assert state.progress.pending_location == "sunny_meadows"


@pytest.mark.parametrize(
    ("current_mode", "expected_mode"),
    [
        (GameMode.MAP, GameMode.MENU),
        (GameMode.MAP_OVERLAY, GameMode.GAME),
    ],
)
def test_back_from_map_uses_context(
    current_mode: GameMode, expected_mode: GameMode
) -> None:
    state = GameState[object](mode=current_mode)
    controller = GameController(state)

    controller.handle_map(MapEvent(MapAction.BACK))

    assert state.mode is expected_mode
