import os
from collections.abc import Iterator

import pygame
import pytest

from game.app import GameRuntime

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")


@pytest.fixture(scope="session", autouse=True)
def pygame_runtime() -> Iterator[None]:
    """Provide one isolated, headless Pygame runtime for the test session."""
    pygame.init()
    pygame.display.set_mode((1, 1))
    yield
    pygame.quit()


@pytest.fixture
def game_runtime(pygame_runtime: None) -> Iterator[GameRuntime]:
    """Create a runtime while keeping global Pygame cleanup in one fixture."""
    pygame.event.clear()
    runtime = GameRuntime(is_web=False)
    yield runtime
    pygame.event.clear()
    runtime.audio_service.stop_music()
