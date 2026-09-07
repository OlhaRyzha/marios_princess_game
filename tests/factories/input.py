from dataclasses import dataclass, field

import pygame

from game.systems.input_state import InputState


@dataclass(slots=True)
class FakeInputSource:
    state: InputState = field(default_factory=InputState)

    def handle_event(self, event: pygame.event.Event) -> None:
        return None

    def read(self) -> InputState:
        return self.state
