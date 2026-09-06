import os
from collections.abc import Iterator

import pygame
import pytest

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
