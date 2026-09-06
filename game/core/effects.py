import pygame

from game.utils.constants import CONFETTI_TIME_MS, HIT_SPARK_TIME_MS


class HitSpark(pygame.sprite.Sprite):
    def __init__(self, pos: tuple[int, int]):
        super().__init__()
        self.pos = pygame.Vector2(pos)
        self.start_ms = pygame.time.get_ticks()
        self.image = pygame.Surface((1, 1), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=pos)

    def update(self, dt: float):
        if pygame.time.get_ticks() - self.start_ms >= HIT_SPARK_TIME_MS:
            self.kill()

    def draw(self, surface: pygame.Surface, camera_x: float):
        age = pygame.time.get_ticks() - self.start_ms
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

    def __init__(self, rect: pygame.Rect):
        super().__init__()
        self.rect = rect.copy()
        self.start_ms = pygame.time.get_ticks()
        self.particles = []
        colors = [
            (255, 95, 95),
            (255, 190, 70),
            (120, 210, 120),
            (90, 170, 255),
            (200, 120, 255),
        ]
        import random

        for _ in range(80):
            x = random.randint(self.rect.left + 40, self.rect.right - 40)
            y = self.rect.top - 10
            vx = random.uniform(-1.2, 1.2)
            vy = random.uniform(0.2, 1.2)
            size = random.randint(3, 6)
            col = random.choice(colors)
            self.particles.append([x, y, vx, vy, size, col])

    def update(self, dt: float):
        if pygame.time.get_ticks() - self.start_ms >= CONFETTI_TIME_MS:
            self.kill()
            return

        for p in self.particles:
            p[0] += p[2] * 60 * dt
            p[1] += p[3] * 60 * dt
            p[3] += 0.02

    def draw(self, surface: pygame.Surface, camera_x: float):
        for x, y, _, _, s, col in self.particles:
            pygame.draw.rect(surface, col, (int(x - camera_x), int(y), s, s))
