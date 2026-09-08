import random

import pygame

from game.gameplay.effects import ConfettiBurst, HitSpark
from game.utils.constants import CONFETTI_TIME_MS, HIT_SPARK_TIME_MS
from tests.factories.time import FakeTimeSource


def test_hit_spark_expires_at_its_deadline(pygame_runtime: None) -> None:
    time_source = FakeTimeSource()
    spark = HitSpark((20, 30), time_source=time_source)
    sprites: pygame.sprite.Group = pygame.sprite.Group()
    sprites.add(spark)

    time_source.advance(HIT_SPARK_TIME_MS - 1)
    sprites.update(0.0)
    assert spark.alive()

    time_source.advance(1)
    sprites.update(0.0)
    assert not spark.alive()


def test_confetti_expires_at_its_deadline(pygame_runtime: None) -> None:
    time_source = FakeTimeSource()
    confetti = ConfettiBurst(
        pygame.Rect(0, 0, 200, 100),
        time_source=time_source,
        rng=random.Random(42),
    )
    sprites: pygame.sprite.Group = pygame.sprite.Group()
    sprites.add(confetti)

    time_source.advance(CONFETTI_TIME_MS)
    sprites.update(0.0)

    assert not confetti.alive()


def test_confetti_is_repeatable_with_the_same_seed(pygame_runtime: None) -> None:
    rect = pygame.Rect(0, 0, 200, 100)
    first = ConfettiBurst(
        rect,
        time_source=FakeTimeSource(),
        rng=random.Random(2026),
    )
    second = ConfettiBurst(
        rect,
        time_source=FakeTimeSource(),
        rng=random.Random(2026),
    )

    assert first.particles == second.particles
