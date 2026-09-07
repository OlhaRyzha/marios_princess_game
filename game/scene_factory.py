import random
from collections.abc import Callable
from dataclasses import dataclass

import pygame

from game.core.demo_scene import DemoScene
from game.data.locations import LocationName
from game.services.audio import AudioService
from game.systems.input_state import InputSource
from game.systems.time_source import TimeSource


@dataclass(slots=True)
class SceneFactory:
    screen: pygame.Surface
    time_source: TimeSource
    input_source: InputSource
    rng: random.Random
    audio_service: AudioService

    def create_game_scene(
        self,
        location: LocationName,
        *,
        on_location_completed: Callable[[LocationName], None],
    ) -> DemoScene:
        return DemoScene(
            self.screen,
            location=location,
            time_source=self.time_source,
            input_source=self.input_source,
            rng=self.rng,
            audio_service=self.audio_service,
            on_location_completed=on_location_completed,
        )
