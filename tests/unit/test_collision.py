from game.gameplay.collision import collide_mask
from tests.factories.sprites import make_masked_sprite


def test_collide_mask_detects_overlapping_opaque_pixels(
    pygame_runtime: None,
) -> None:
    first = make_masked_sprite(topleft=(0, 0))
    second = make_masked_sprite(topleft=(5, 5))

    assert collide_mask(first, second)


def test_collide_mask_ignores_overlapping_transparent_pixels(
    pygame_runtime: None,
) -> None:
    first = make_masked_sprite(topleft=(0, 0))
    second = make_masked_sprite(topleft=(5, 5), opaque=False)

    assert not collide_mask(first, second)
