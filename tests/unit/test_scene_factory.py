import random

import pygame

from game.i18n import Localizer
from game.scene_factory import SceneFactory
from game.utils.constants import MUSIC_LEVEL
from tests.factories.audio import RecordingAudioService
from tests.factories.input import FakeInputSource
from tests.factories.time import FakeTimeSource


def test_scene_factory_connects_dependencies_and_starts_level_music(
    pygame_runtime: None,
) -> None:
    screen = pygame.display.get_surface()
    assert screen is not None
    time_source = FakeTimeSource()
    input_source = FakeInputSource()
    rng = random.Random(2026)
    audio_service = RecordingAudioService()
    factory = SceneFactory(
        screen=screen,
        time_source=time_source,
        input_source=input_source,
        rng=rng,
        audio_service=audio_service,
        localizer=Localizer(),
    )

    scene = factory.create_game_scene(
        "sunny_meadows", on_location_completed=lambda location: None
    )

    assert scene.time_source is time_source
    assert scene.input_source is input_source
    assert scene.rng is rng
    assert scene.audio_service is audio_service
    assert audio_service.stop_count == 1
    assert audio_service.played_tracks == [(MUSIC_LEVEL, True)]
