import random

import pygame

from game.core.collectible import Collectible
from game.data.collectibles import COLLECTIBLE_SETS, CollectibleSet
from game.data.locations import LocationName
from game.i18n import Localizer
from game.utils.images import scale_to_height
from game.utils.paths import resolve_project_path


class CollectibleSystem:
    def __init__(self, *, rng: random.Random, localizer: Localizer) -> None:
        self.rng = rng
        self.localizer = localizer
        self.sprites: pygame.sprite.Group = pygame.sprite.Group()
        self.setup: CollectibleSet | None = None
        self.collected = 0
        self.icon: pygame.Surface | None = None

    @property
    def goal(self) -> int:
        return len(self.setup.positions) if self.setup else 0

    @property
    def label(self) -> str:
        return self.localizer.resolve(self.setup.label) if self.setup else ""

    @property
    def hint(self) -> str:
        return self.localizer.resolve(self.setup.hint) if self.setup else ""

    @property
    def progress(self) -> tuple[int, int] | None:
        return (self.collected, self.goal) if self.goal else None

    @property
    def progress_text(self) -> str:
        return f"{self.label}: {self.collected}/{self.goal}" if self.goal else ""

    @property
    def complete(self) -> bool:
        return self.goal == 0 or self.collected >= self.goal

    def load(self, location: LocationName) -> None:
        self.sprites.empty()
        self.setup = COLLECTIBLE_SETS.get(location)
        self.collected = 0
        self.icon = None
        if self.setup is None:
            return

        world_surface, icon_surface = self._load_surfaces(self.setup)
        for position in self.setup.positions:
            self.sprites.add(
                Collectible(
                    self.setup.kind,
                    position,
                    rng=self.rng,
                    surface=world_surface,
                )
            )
        self.icon = (
            icon_surface.copy()
            if icon_surface is not None
            else Collectible.icon(self.setup.kind, size=26)
        )

    def collect(self, player_rect: pygame.Rect) -> list[tuple[int, int]]:
        hits = [item for item in self.sprites if player_rect.colliderect(item.rect)]
        positions = [item.rect.center for item in hits]
        for item in hits:
            item.kill()
        self.collected = min(self.goal, self.collected + len(hits))
        return positions

    @staticmethod
    def _load_surfaces(
        setup: CollectibleSet,
    ) -> tuple[pygame.Surface | None, pygame.Surface | None]:
        if setup.image_path is None:
            return None, None
        try:
            raw = pygame.image.load(
                resolve_project_path(setup.image_path)
            ).convert_alpha()
        except (FileNotFoundError, OSError, pygame.error):
            return None, None
        return (
            scale_to_height(raw, setup.world_height),
            scale_to_height(raw, setup.icon_height),
        )
