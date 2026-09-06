import pygame

from game.systems.animation import Animation


def test_animation_repeats_frames(pygame_runtime: None) -> None:
    frames = [pygame.Surface((1, 1)), pygame.Surface((2, 2))]
    animation = Animation(frames, fps=2, loop=True)

    animation.update(1.0)

    assert animation.image() is frames[0]


def test_non_looping_animation_stays_on_last_frame(pygame_runtime: None) -> None:
    frames = [pygame.Surface((1, 1)), pygame.Surface((2, 2))]
    animation = Animation(frames, fps=2, loop=False)

    animation.update(10.0)

    assert animation.image() is frames[-1]
