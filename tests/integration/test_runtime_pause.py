import pygame
import pytest

from game.app import GameRuntime
from game.data.start_menu import PAUSE_MENU_ITEMS
from game.scenes.demo_scene import DemoScene
from game.state import GameMode


def test_escape_pauses_and_resumes_game(game_runtime: GameRuntime) -> None:
    game_runtime.state.mode = GameMode.GAME

    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
    game_runtime.tick()

    assert game_runtime.state.mode is GameMode.MENU_PAUSE

    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
    game_runtime.tick()

    assert game_runtime.state.mode is GameMode.GAME


def test_pause_menu_has_continue_action(game_runtime: GameRuntime) -> None:
    game_runtime.state.mode = GameMode.MENU_PAUSE

    game_runtime.tick()

    assert game_runtime.menu.items == list(PAUSE_MENU_ITEMS)


@pytest.mark.parametrize("mode", [GameMode.MENU_PAUSE, GameMode.MAP_OVERLAY])
def test_overlay_modes_do_not_update_scene(
    game_runtime: GameRuntime, mode: GameMode
) -> None:
    scene = DemoScene(
        game_runtime.screen,
        time_source=game_runtime.time_source,
        input_source=game_runtime.input_source,
        rng=game_runtime.rng,
        audio_service=game_runtime.audio_service,
    )
    scene.player.on_ground = False
    scene.player.pos.y = 300
    scene.player.vel.y = 5
    game_runtime.state.scene = scene
    game_runtime.state.mode = mode
    position_before_pause = scene.player.pos.copy()

    game_runtime.tick()

    assert scene.player.pos == position_before_pause
