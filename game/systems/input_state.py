from dataclasses import dataclass
from typing import Protocol

import pygame


@dataclass(frozen=True, slots=True)
class InputState:
    left: bool = False
    right: bool = False
    down: bool = False
    jump: bool = False
    run: bool = False
    attack: bool = False
    celebrate: bool = False
    hurt: bool = False
    cry: bool = False


class InputSource(Protocol):
    def handle_event(self, event: pygame.event.Event) -> None: ...

    def read(self) -> InputState: ...


class PygameInputSource:
    def __init__(self) -> None:
        self._pressed_actions: set[int] = set()

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            self._pressed_actions.add(event.key)

    def read(self) -> InputState:
        keys = pygame.key.get_pressed()
        pressed_actions = self._pressed_actions.copy()
        self._pressed_actions.clear()
        return InputState(
            left=bool(keys[pygame.K_LEFT] or keys[pygame.K_a]),
            right=bool(keys[pygame.K_RIGHT] or keys[pygame.K_d]),
            down=bool(keys[pygame.K_DOWN] or keys[pygame.K_s]),
            jump=bool(
                keys[pygame.K_SPACE]
                or keys[pygame.K_w]
                or keys[pygame.K_UP]
                or pressed_actions.intersection(
                    {pygame.K_SPACE, pygame.K_w, pygame.K_UP}
                )
            ),
            run=bool(keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]),
            attack=bool(keys[pygame.K_j] or pygame.K_j in pressed_actions),
            celebrate=bool(keys[pygame.K_k] or pygame.K_k in pressed_actions),
            hurt=bool(keys[pygame.K_h] or pygame.K_h in pressed_actions),
            cry=bool(keys[pygame.K_f] or pygame.K_f in pressed_actions),
        )
