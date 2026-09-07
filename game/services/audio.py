import logging
from pathlib import Path
from typing import Protocol

import pygame

from game.utils.constants import MUSIC_VOLUME
from game.utils.paths import resolve_project_path

logger = logging.getLogger(__name__)


class AudioService(Protocol):
    def arm(self) -> bool: ...

    def play_music(self, path: str | Path, *, loop: bool = True) -> None: ...

    def stop_music(self) -> None: ...


class PygameAudioService:
    def arm(self) -> bool:
        if pygame.mixer.get_init():
            return True
        try:
            pygame.mixer.init()
        except pygame.error as error:
            logger.warning("Audio is unavailable: %s", error)
            return False
        return True

    def play_music(self, path: str | Path, *, loop: bool = True) -> None:
        if not self.arm():
            return
        resolved_path = resolve_project_path(path)
        try:
            pygame.mixer.music.load(resolved_path)
            pygame.mixer.music.set_volume(MUSIC_VOLUME)
            pygame.mixer.music.play(-1 if loop else 0)
        except (FileNotFoundError, OSError, pygame.error) as error:
            logger.warning("Could not play music %s: %s", resolved_path, error)

    def stop_music(self) -> None:
        if not pygame.mixer.get_init():
            return
        try:
            pygame.mixer.music.stop()
        except pygame.error as error:
            logger.warning("Could not stop music: %s", error)
