import random

import pygame

from game.app import GameRuntime
from game.data.bosses import BOSS_ROSTER
from game.i18n import Localizer
from game.scene_factory import SceneFactory
from game.state import GameMode
from game.systems.input_state import InputState
from tests.factories.audio import RecordingAudioService
from tests.factories.input import FakeInputSource
from tests.factories.time import FakeTimeSource


def test_attack_input_shoots_heart_during_boss_fight(
    pygame_runtime: None,
) -> None:
    screen = pygame.display.get_surface()
    assert screen is not None
    input_source = FakeInputSource()
    scene = SceneFactory(
        screen=screen,
        time_source=FakeTimeSource(),
        input_source=input_source,
        rng=random.Random(2026),
        audio_service=RecordingAudioService(),
        localizer=Localizer(),
    ).create_game_scene("sunny_meadows", on_location_completed=lambda location: None)
    scene.boss_preview.open(BOSS_ROSTER["sunny_meadows"])
    scene.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
    input_source.state = InputState(attack=True)

    scene.update(1 / 60)

    assert scene.mode == "boss"
    assert len(scene.projectiles) == 1

    boss = next(iter(scene.boss_group))
    projectile = next(iter(scene.projectiles))
    projectile.rect.center = boss.rect.center
    health_before_hit = boss.health
    input_source.state = InputState()

    scene.update(1 / 60)

    assert boss.health == health_before_hit - 1
    assert len(scene.projectiles) == 0


def test_runtime_does_not_lose_a_short_attack_keypress(
    game_runtime: GameRuntime,
) -> None:
    scene = game_runtime.scene_factory.create_game_scene(
        "sunny_meadows", on_location_completed=lambda location: None
    )
    scene.boss_preview.open(BOSS_ROSTER["sunny_meadows"])
    scene.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
    game_runtime.state.scene = scene
    game_runtime.state.mode = GameMode.GAME
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_j))
    pygame.event.post(pygame.event.Event(pygame.KEYUP, key=pygame.K_j))

    game_runtime.tick()

    assert len(scene.projectiles) == 1
