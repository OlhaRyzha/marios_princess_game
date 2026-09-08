import random
from typing import cast

import pygame

from game.core.collectible_system import CollectibleSystem
from game.core.collision import CollisionSprite, collide_mask
from game.core.effects import HitSpark
from game.core.obstacle_factory import boss_gate_position, build_obstacles
from game.core.player import Princess
from game.data.locations import LocationName
from game.i18n import Localizer
from game.state import SceneMode
from game.systems.time_source import TimeSource
from game.utils.constants import DAMAGE_PER_HIT, GROUND_Y, OBSTACLE_SCALE


class DemoLevel:
    """Own the sprites and exploration rules for one gameplay level."""

    START_X = 240

    def __init__(
        self,
        *,
        screen_height: int,
        location: LocationName,
        time_source: TimeSource,
        rng: random.Random,
        localizer: Localizer,
    ) -> None:
        self.screen_height = screen_height
        self.rng = rng
        self.player = Princess((self.START_X, GROUND_Y), time_source=time_source)
        self.all_sprites: pygame.sprite.Group = pygame.sprite.Group()
        self.all_sprites.add(self.player)
        self.obstacles: pygame.sprite.Group = pygame.sprite.Group()
        self.boss_group: pygame.sprite.Group = pygame.sprite.Group()
        self.fx_group: pygame.sprite.Group = pygame.sprite.Group()
        self.projectiles: pygame.sprite.Group = pygame.sprite.Group()
        self.collectible_system = CollectibleSystem(rng=rng, localizer=localizer)
        self.collectibles = self.collectible_system.sprites
        self.boss_gate_x = 0
        self.boss_trigger_rect = pygame.Rect(0, 0, 48, screen_height)
        self.load(location)

    def load(self, location: LocationName) -> None:
        """Replace level objects and collectibles for a location."""
        old_obstacles = tuple(self.obstacles.sprites())
        if old_obstacles:
            self.all_sprites.remove(*old_obstacles)
        self.obstacles.empty()

        new_obstacles, max_right = build_obstacles(
            location=location,
            start_x=self.START_X,
            scale=OBSTACLE_SCALE,
            rng=self.rng,
        )
        if new_obstacles:
            self.obstacles.add(*new_obstacles)
            self.all_sprites.add(*new_obstacles)

        self.collectible_system.load(location)
        self.boss_gate_x = boss_gate_position(max_right)
        self.boss_trigger_rect = pygame.Rect(
            self.boss_gate_x, 0, 48, self.screen_height
        )

    def reset_player(self) -> None:
        """Return the player to the beginning of the current level."""
        self.player.pos.update(self.START_X, GROUND_Y)
        self.player.rect.midbottom = (
            int(self.player.pos.x),
            int(self.player.pos.y),
        )

    def update_exploration(self, mode: SceneMode, time_source: TimeSource) -> None:
        """Resolve obstacle damage and collectible pickup during exploration."""
        if mode is not SceneMode.EXPLORE:
            return
        hits = [
            obstacle
            for obstacle in self.obstacles
            if collide_mask(
                cast(CollisionSprite, self.player),
                cast(CollisionSprite, obstacle),
            )
        ]
        if hits and self.player.can_take_damage():
            self.player.take_damage(DAMAGE_PER_HIT)
            self.player.pos.x += -18 if self.player.dir > 0 else 18
            self.player.rect.x = int(self.player.pos.x)

        for position in self.collectible_system.collect(self.player.rect):
            self.fx_group.add(HitSpark(position, time_source=time_source))

    def reached_boss_gate(self) -> bool:
        """Return whether the player has reached the boss entrance."""
        return self.player.rect.right >= self.boss_trigger_rect.left
