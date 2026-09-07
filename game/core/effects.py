import random
from dataclasses import dataclass

import pygame

from game.systems.time_source import TimeSource
from game.utils.constants import CONFETTI_TIME_MS, HIT_SPARK_TIME_MS

Color = tuple[int, int, int]


@dataclass(slots=True)
class ConfettiParticle:
    x: float
    y: float
    velocity_x: float
    velocity_y: float
    size: int
    color: Color


class HitSpark(pygame.sprite.Sprite):
    def __init__(self, pos: tuple[int, int], *, time_source: TimeSource):
        super().__init__()
        self.time_source = time_source
        self.pos = pygame.Vector2(pos)
        self.start_ms = self.time_source.now_ms()
        self.image = pygame.Surface((1, 1), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=pos)

    def update(self, dt: float):
        if self.time_source.now_ms() - self.start_ms >= HIT_SPARK_TIME_MS:
            self.kill()

    def draw(self, surface: pygame.Surface, camera_x: float):
        age = self.time_source.now_ms() - self.start_ms
        t = max(0.0, min(1.0, age / HIT_SPARK_TIME_MS))
        cx = int(self.pos.x - camera_x)
        cy = int(self.pos.y)

        r = int(8 + 22 * t)
        alpha = int(220 * (1 - t))
        color = (255, 230, 120, alpha)
        circle = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(circle, color, (r + 1, r + 1), r, width=3)
        surface.blit(circle, circle.get_rect(center=(cx, cy)))

        rays = 6
        ray_len = int(8 + 26 * (1 - t))
        ray_surf = pygame.Surface((ray_len, 2), pygame.SRCALPHA)
        ray_surf.fill((255, 200, 100, alpha))
        for i in range(rays):
            ang = i * (360 / rays)
            rot = pygame.transform.rotate(ray_surf, ang)
            surface.blit(rot, rot.get_rect(center=(cx, cy)))


class ConfettiBurst(pygame.sprite.Sprite):
    def __init__(
        self,
        rect: pygame.Rect,
        *,
        time_source: TimeSource,
        rng: random.Random,
    ):
        super().__init__()
        self.time_source = time_source
        self.image = pygame.Surface((1, 1), pygame.SRCALPHA)
        self.rect = rect.copy()
        self.start_ms = self.time_source.now_ms()
        self.particles: list[ConfettiParticle] = []
        colors: tuple[Color, ...] = (
            (255, 95, 95),
            (255, 190, 70),
            (120, 210, 120),
            (90, 170, 255),
            (200, 120, 255),
        )
        for _ in range(80):
            x = rng.randint(self.rect.left + 40, self.rect.right - 40)
            y = self.rect.top - 10
            vx = rng.uniform(-1.2, 1.2)
            vy = rng.uniform(0.2, 1.2)
            size = rng.randint(3, 6)
            col = rng.choice(colors)
            self.particles.append(ConfettiParticle(x, y, vx, vy, size, col))

    def update(self, dt: float):
        if self.time_source.now_ms() - self.start_ms >= CONFETTI_TIME_MS:
            self.kill()
            return

        for particle in self.particles:
            particle.x += particle.velocity_x * 60 * dt
            particle.y += particle.velocity_y * 60 * dt
            particle.velocity_y += 0.02

    def draw(self, surface: pygame.Surface, camera_x: float):
        for particle in self.particles:
            pygame.draw.rect(
                surface,
                particle.color,
                (
                    int(particle.x - camera_x),
                    int(particle.y),
                    particle.size,
                    particle.size,
                ),
            )
