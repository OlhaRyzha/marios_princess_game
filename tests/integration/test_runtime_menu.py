import pygame

from game.app import GameRuntime
from game.state import GameMode
from tests.factories.audio import RecordingAudioService


def test_main_menu_starts_game_scene(game_runtime: GameRuntime) -> None:
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))

    game_runtime.tick()

    assert game_runtime.state.mode is GameMode.GAME
    assert game_runtime.state.scene is not None
    assert game_runtime.state.scene.time_source is game_runtime.time_source
    assert game_runtime.state.scene.input_source is game_runtime.input_source
    assert game_runtime.state.scene.rng is game_runtime.rng
    assert game_runtime.state.scene.audio_service is game_runtime.audio_service


def test_controls_modal_closes_without_leaving_menu(
    game_runtime: GameRuntime,
) -> None:
    game_runtime.menu.selected = 2
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))

    game_runtime.tick()

    assert game_runtime.menu.controls_open
    assert game_runtime.state.mode is GameMode.MENU

    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
    game_runtime.tick()

    assert not game_runtime.menu.controls_open
    assert game_runtime.state.mode is GameMode.MENU


def test_quit_event_stops_runtime(game_runtime: GameRuntime) -> None:
    pygame.event.post(pygame.event.Event(pygame.QUIT))

    game_runtime.tick()

    assert not game_runtime.state.running


def test_web_input_arms_audio_once(game_runtime: GameRuntime) -> None:
    audio_service = RecordingAudioService()
    game_runtime.input_adapter.is_web = True
    game_runtime.input_adapter.audio_service = audio_service
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_x))
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_y))

    game_runtime.tick()

    assert game_runtime.state.audio_armed
    assert audio_service.armed
    assert audio_service.arm_count == 1
