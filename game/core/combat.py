from collections.abc import Callable
from typing import Protocol, cast

import pygame
from pygame.mask import Mask
from pygame.math import Vector2

from game.core.effects import HitSpark
from game.utils.constants import (
    ATTACK_DAMAGE,
    ATTACK_HIT_COOLDOWN_MS,
    DAMAGE_PER_HIT,
    LEVEL_WIDTH,
)


class PlayerSprite(Protocol):
    rect: pygame.Rect
    state: str
    dir: int
    pos: Vector2
    mask: Mask

    def take_damage(self, amount: int = ...) -> None: ...

    def can_take_damage(self) -> bool: ...

    def set_state(self, s: str, timer: float = 0.0) -> None: ...


class BossSprite(Protocol):
    rect: pygame.Rect
    mask: Mask
    health: int

    def kill(self) -> None: ...

    def take_damage(self, amount: int, *, knockback_dir: int) -> bool: ...


class ProjectileSprite(Protocol):
    rect: pygame.Rect

    def kill(self) -> None: ...


SpriteLike = pygame.sprite.Sprite | PlayerSprite | BossSprite | ProjectileSprite


class CombatSystem:

    def __init__(
        self,
        player: PlayerSprite,
        boss_group: pygame.sprite.Group,
        projectiles: pygame.sprite.Group,
        fx_group: pygame.sprite.Group,
        *,
        heart_cooldown_ms: int = ATTACK_HIT_COOLDOWN_MS,
        on_boss_defeated: Callable[[], None] | None = None,
    ) -> None:
        self.player: PlayerSprite = player
        self.boss_group = boss_group
        self.projectiles = projectiles
        self.fx_group = fx_group

        self._last_melee_hit_ms = -10_000
        self._last_heart_shot_ms = -10_000
        self._heart_cooldown_ms = heart_cooldown_ms
        self.on_boss_defeated = on_boss_defeated

        self._victory_fired = False
        self._victory_ready_at: int | None = None

    def start_boss(self, boss_actor: BossSprite) -> None:
        self.boss_group.empty()
        self.boss_group.add(boss_actor)
        self._victory_fired = False
        self._victory_ready_at = None

    def update(self, dt: float) -> None:
        self.boss_group.update(dt, player_x=self.player.pos.x)

        self.projectiles.update(dt)
        for pr in list(self.projectiles):
            projectile = cast(ProjectileSprite, pr)
            if projectile.rect.right < 0 or projectile.rect.left > LEVEL_WIDTH:
                projectile.kill()

        if self._victory_fired and self._victory_ready_at is not None:
            if self._now() >= self._victory_ready_at:
                self._victory_ready_at = None
                if self.on_boss_defeated:
                    self.on_boss_defeated()

    def update_boss_phase(self) -> None:
        self._handle_melee_hits()
        self.maybe_shoot_heart()
        self._handle_heart_hits()
        self._handle_boss_body_collision()

    def _now(self) -> int:
        return pygame.time.get_ticks()

    def _collide_mask(self, a: SpriteLike, b: SpriteLike) -> bool:
        ma = getattr(a, "mask", None)
        mb = getattr(b, "mask", None)
        if ma is not None and mb is not None:
            rect_a = cast(pygame.Rect, a.rect)
            rect_b = cast(pygame.Rect, b.rect)
            offset = (rect_b.x - rect_a.x, rect_b.y - rect_a.y)
            return ma.overlap(mb, offset) is not None
        rect_a = cast(pygame.Rect, a.rect)
        rect_b = cast(pygame.Rect, b.rect)
        return rect_a.colliderect(rect_b)

    def _maybe_call_victory(self, boss: BossSprite) -> None:
        if self._victory_fired:
            return
        if getattr(boss, "health", 1) <= 0:
            boss.kill()
            self._victory_fired = True
            celebrate_duration_ms = 1600
            self.player.set_state("celebrate", timer=celebrate_duration_ms / 1000.0)
            self._victory_ready_at = self._now() + celebrate_duration_ms

    def _handle_melee_hits(self) -> None:
        if not self.boss_group:
            return
        now = self._now()
        if self.player.state != "attack":
            return
        if now - self._last_melee_hit_ms < ATTACK_HIT_COOLDOWN_MS:
            return

        boss = next(iter(self.boss_group), None)
        if not boss:
            return
        boss_sprite = cast(BossSprite, boss)

        if self._collide_mask(self.player, boss_sprite):
            self._last_melee_hit_ms = now
            impact_x = max(
                min(self.player.rect.centerx, boss_sprite.rect.right),
                boss_sprite.rect.left,
            )
            impact_y = (self.player.rect.centery + boss_sprite.rect.centery) // 2
            kb_dir = 1 if self.player.dir > 0 else -1

            if boss_sprite.take_damage(ATTACK_DAMAGE, knockback_dir=kb_dir):
                self.fx_group.add(HitSpark((impact_x, impact_y)))

            self._maybe_call_victory(boss_sprite)

    def maybe_shoot_heart(self) -> None:
        if self.player.state != "attack":
            return
        now = self._now()
        if now - self._last_heart_shot_ms < self._heart_cooldown_ms:
            return
        self._last_heart_shot_ms = now

        direction = 1 if self.player.dir > 0 else -1
        start_x = self.player.rect.centerx + 30 * direction
        start_y = self.player.rect.centery - 40

        from game.core.heart_projectile import HeartProjectile

        self.projectiles.add(HeartProjectile(start_x, start_y, direction=direction))

    def _handle_heart_hits(self) -> None:
        if not self.projectiles or not self.boss_group:
            return

        collisions = pygame.sprite.groupcollide(
            self.projectiles, self.boss_group, True, False, collided=self._collide_mask
        )
        if not collisions:
            return

        hit_bosses: set[BossSprite] = set()
        for bosses in collisions.values():
            for boss in bosses:
                hit_bosses.add(cast(BossSprite, boss))

        for boss in hit_bosses:
            impact_x = max(min(boss.rect.centerx, boss.rect.right), boss.rect.left)
            impact_y = boss.rect.centery
            self.fx_group.add(HitSpark((impact_x, impact_y)))
            boss.take_damage(ATTACK_DAMAGE, knockback_dir=0)
            self._maybe_call_victory(boss)

    def _handle_boss_body_collision(self) -> None:
        if not self.boss_group:
            return

        boss = next(iter(self.boss_group), None)
        if not boss:
            return

        boss_sprite = cast(BossSprite, boss)
        if self._collide_mask(self.player, boss_sprite):
            if self.player.can_take_damage():
                self.player.take_damage(DAMAGE_PER_HIT)
            self.player.set_state("cry", timer=0.6)
