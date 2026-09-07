import pygame

from game.systems.input_state import PygameInputSource


def test_short_attack_press_is_consumed_by_next_update(
    pygame_runtime: None,
) -> None:
    input_source = PygameInputSource()
    input_source.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_j))
    input_source.handle_event(pygame.event.Event(pygame.KEYUP, key=pygame.K_j))

    first_update = input_source.read()
    second_update = input_source.read()

    assert first_update.attack
    assert not second_update.attack
