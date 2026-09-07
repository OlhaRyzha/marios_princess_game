import pygame

from game.core.finale import FinaleCinematic


def test_finale_becomes_ready_after_duration(pygame_runtime: None) -> None:
    finale = FinaleCinematic(duration_ms=100, hug_candidates=())

    assert not finale.is_running()
    assert not finale.ready_for_modal(100)

    finale.start(50)

    assert finale.is_running()
    assert not finale.ready_for_modal(149)
    assert finale.ready_for_modal(150)

    finale.reset()
    assert not finale.is_running()


def test_finale_draws_with_fallback_asset(pygame_runtime: None) -> None:
    finale = FinaleCinematic(hug_candidates=("assets/missing-hug.png",))
    surface = pygame.Surface((320, 180))

    finale.draw(surface)

    assert finale._hug_img is not None
    assert surface.get_at((0, 0)) != pygame.Color(0, 0, 0, 255)
