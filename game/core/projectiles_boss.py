from __future__ import annotations
import math
import pygame
from game.utils import LEVEL_WIDTH, GROUND_Y


class GroundWave(pygame.sprite.Sprite):
    """Плоска хвиля по землі від тупоту."""

    SPEED = 5
    WIDTH = 38
    HEIGHT = 16
    DAMAGE = 1

    def __init__(self, x: int, direction: int):
        super().__init__()
        self.image = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(
            self.image, (190, 90, 90), (0, 0, self.WIDTH, self.HEIGHT), border_radius=6
        )
        self.rect = self.image.get_rect(midbottom=(x, GROUND_Y))
        self.velx = self.SPEED * (1 if direction >= 0 else -1)

    def update(self, dt: float):
        self.rect.x += int(self.velx)
        if self.rect.right < 0 or self.rect.left > LEVEL_WIDTH:
            self.kill()


class Pinecone(pygame.sprite.Sprite):
    """Шишка з дугою польоту (парабола)."""

    GRAVITY = 0.35
    DAMAGE = 1

    def __init__(self, x: int, y: int, direction: int):
        super().__init__()
        self.image = pygame.Surface((18, 18), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (150, 100, 60), (9, 9), 8)
        self.rect = self.image.get_rect(center=(x, y))
        self.vx = 3.6 * (1 if direction >= 0 else -1)
        self.vy = -6.0

    def update(self, dt: float):
        self.vy += self.GRAVITY
        self.rect.x += int(self.vx)
        self.rect.y += int(self.vy)
        if self.rect.bottom >= GROUND_Y:
            self.rect.bottom = GROUND_Y
            self.vy *= -0.45
            self.vx *= 0.88
            if abs(self.vy) < 1.6:
                self.kill()
        if self.rect.right < 0 or self.rect.left > LEVEL_WIDTH:
            self.kill()


class BatMinion(pygame.sprite.Sprite):
    """Малий кажан: підлітає хвилями, вразливий під час зависання."""

    SPEED_X = 2.3
    AMPL = 18
    DAMAGE = 1

    def __init__(self, x: int, y: int, towards_right: bool):
        super().__init__()
        self.image = pygame.Surface((22, 14), pygame.SRCALPHA)
        pygame.draw.polygon(
            self.image,
            (130, 200, 230),
            [(0, 7), (8, 0), (14, 7), (22, 0), (22, 14), (0, 14)],
        )
        self.rect = self.image.get_rect(center=(x, y))
        self.dir = 1 if towards_right else -1
        self._t = 0.0

    def update(self, dt: float):
        self._t += dt
        self.rect.x += int(self.SPEED_X * self.dir)
        self.rect.y += int(self.AMPL * 0.06 * math.sin(self._t * 8.0))
        if self.rect.right < 0 or self.rect.left > LEVEL_WIDTH:
            self.kill()
