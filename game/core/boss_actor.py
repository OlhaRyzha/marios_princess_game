import pygame

from game.utils import (
    GROUND_Y,
    BOSS_MAX_HEALTH,
    BOSS_SCALE,
    BOSS_SPEED,
    BOSS_JUMP_V,
    BOSS_HIT_COOLDOWN_MS,
    GRAVITY,
    load_image,
)


class BossActor(pygame.sprite.Sprite):

    def __init__(self, *, name: str, image_path: str, x: int):
        super().__init__()
        self.name = name
        raw: pygame.Surface = load_image(image_path)
        w, h = raw.get_size()
        self.base_image: pygame.Surface = pygame.transform.smoothscale(
            raw, (int(w * BOSS_SCALE), int(h * BOSS_SCALE))
        )
        self.image: pygame.Surface = self.base_image
        self.rect: pygame.Rect = self.image.get_rect(midbottom=(x, GROUND_Y))
        self.mask: pygame.mask.Mask = pygame.mask.from_surface(self.image)

        self.max_health = BOSS_MAX_HEALTH
        self.health = self.max_health

        self.vel: pygame.Vector2 = pygame.Vector2(0, 0)
        self.dir = -1
        self._t = 0.0
        self._jump_cd = 0.0
        self._last_hit_ms = -10_000
        self._flash_ms_left = 0

    def can_take_damage(self) -> bool:
        return (pygame.time.get_ticks() - self._last_hit_ms) >= BOSS_HIT_COOLDOWN_MS

    def take_damage(self, amount: int, *, knockback_dir: int = 0) -> bool:
        if not self.can_take_damage():
            return False
        self.health = max(0, self.health - amount)
        self._last_hit_ms = pygame.time.get_ticks()
        self._flash_ms_left = 120
        self.vel.x += 2.2 * (1 if knockback_dir > 0 else -1)
        self.vel.y = max(self.vel.y, -2.0)
        return True

    def is_dead(self) -> bool:
        return self.health <= 0

    def _ai_move(self, player_x: float, dt: float) -> None:
        self.dir = 1 if player_x > self.rect.centerx else -1
        target_vx = self.dir * BOSS_SPEED
        self.vel.x += (target_vx - self.vel.x) * 0.15

        self._jump_cd -= dt
        if self._jump_cd <= 0 and self.rect.bottom >= GROUND_Y - 0.5:
            self.vel.y = BOSS_JUMP_V
            self._jump_cd = 0.9 + (pygame.time.get_ticks() % 400) / 400.0

    def _physics(self) -> None:
        self.vel.y += GRAVITY
        self.rect.x += int(self.vel.x)
        self.rect.y += int(self.vel.y)

        if self.rect.bottom >= GROUND_Y:
            self.rect.bottom = GROUND_Y
            self.vel.y = 0

    def update(self, dt: float, *, player_x: float):
        self._t += dt
        self._ai_move(player_x, dt)
        self._physics()

        if self._flash_ms_left > 0:
            self._flash_ms_left -= int(dt * 1000)
            flash_img: pygame.Surface = self.base_image.copy()
            flash_img.fill((255, 255, 255, 60), special_flags=pygame.BLEND_RGBA_ADD)
            self.image = flash_img
        else:
            self.image = self.base_image

        self.mask = pygame.mask.from_surface(self.image)

    def draw(self, surface: pygame.Surface, camera_x: float) -> None:
        img: pygame.Surface = self.image
        if self.dir < 0:
            img = pygame.transform.flip(img, True, False)
        surface.blit(img, self.rect.move(-camera_x, 0))
