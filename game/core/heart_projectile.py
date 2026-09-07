import pygame

from game.systems.time_source import TimeSource
from game.utils.images import load_image


class HeartProjectile(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, direction: int, *, time_source: TimeSource):
        super().__init__()
        self.time_source = time_source
        base: pygame.Surface = load_image("assets/princess/attack/heart.png")
        self.image: pygame.Surface = pygame.transform.scale(base, (36, 36))
        self.rect: pygame.Rect = self.image.get_rect(center=(x, y))
        self.speed: int = 8
        self.direction: int = direction
        self.lifetime: int = 2000
        self.spawn_time = self.time_source.now_ms()

    def update(self, dt: float):
        self.rect.x += self.speed * self.direction

        if self.time_source.now_ms() - self.spawn_time > self.lifetime:
            self.kill()
