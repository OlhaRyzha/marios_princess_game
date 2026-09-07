import math
import random
from dataclasses import dataclass

import pygame

from game.data.locations import LocationName
from game.systems.time_source import TimeSource


@dataclass(frozen=True, slots=True)
class FogParticle:
    base_angle: float
    radius_factor: float
    speed: float
    wobble: float
    size: int
    phase: float


class MapFog:
    """Generate and draw animated fog for every map node."""

    def __init__(
        self,
        *,
        locations: list[LocationName],
        rng: random.Random,
        time_source: TimeSource,
        radius: int,
        particle_count: int = 14,
    ) -> None:
        self.time_source = time_source
        self.radius = radius
        self.particles = {
            location: [self._make_particle(rng) for _ in range(particle_count)]
            for location in locations
        }

    @staticmethod
    def _make_particle(rng: random.Random) -> FogParticle:
        return FogParticle(
            base_angle=rng.uniform(0.0, math.tau),
            radius_factor=rng.uniform(0.2, 0.9),
            speed=rng.uniform(0.45, 0.85),
            wobble=rng.uniform(0.55, 0.95),
            size=rng.randint(3, 7),
            phase=rng.uniform(0.0, math.tau),
        )

    def draw(
        self,
        surface: pygame.Surface,
        location: LocationName,
        center: tuple[int, int],
        intensity: float,
    ) -> None:
        nodes = self.particles.get(location)
        if not nodes:
            return
        diameter = self.radius * 2
        fog = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
        now = self.time_source.now_ms() / 1000.0
        margin = 6
        max_radius_squared = (self.radius - margin) ** 2
        for particle in nodes:
            angle = particle.base_angle + now * particle.speed
            phase = now * 0.45 + particle.phase
            orbit = particle.radius_factor * (self.radius - margin)
            x = self.radius + math.cos(angle) * orbit
            y = self.radius + math.sin(angle * particle.wobble + phase) * orbit * 0.86
            if (x - self.radius) ** 2 + (y - self.radius) ** 2 > max_radius_squared:
                continue
            pulse = 0.55 + 0.45 * math.sin(angle * 1.7 + phase)
            alpha = max(18, min(190, int(30 + 140 * intensity * pulse)))
            pygame.draw.circle(
                fog, (255, 255, 255, alpha), (round(x), round(y)), particle.size
            )
        surface.blit(fog, fog.get_rect(center=center))


def lerp(start: float, end: float, factor: float) -> float:
    return start + (end - start) * factor


def mix_color(
    start: tuple[int, int, int],
    end: tuple[int, int, int],
    factor: float,
) -> tuple[int, int, int]:
    return (
        int(lerp(start[0], end[0], factor)),
        int(lerp(start[1], end[1], factor)),
        int(lerp(start[2], end[2], factor)),
    )


def scale_color(color: tuple[int, int, int], factor: float) -> tuple[int, int, int]:
    return (
        max(0, min(255, int(color[0] * factor))),
        max(0, min(255, int(color[1] * factor))),
        max(0, min(255, int(color[2] * factor))),
    )


def make_bubble_surface(
    radius: int,
    palette: tuple[tuple[int, int, int], tuple[int, int, int]],
    *,
    brightness: float = 1.0,
) -> pygame.Surface:
    diameter = radius * 2
    surface = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
    outer_color = scale_color(palette[0], brightness)
    inner_color = scale_color(palette[1], brightness)

    for step in range(radius, 0, -1):
        factor = step / radius
        color = mix_color(inner_color, outer_color, factor**1.45)
        alpha = max(20, min(235, int(160 * (1 - factor**1.8) + 30)))
        pygame.draw.circle(surface, (*color, alpha), (radius, radius), step)

    clouds = (
        (-0.35, 0.15, 0.55, int(52 * brightness)),
        (0.28, -0.20, 0.42, int(40 * brightness)),
        (0.05, 0.35, 0.35, int(32 * brightness)),
    )
    for offset_x, offset_y, scale, alpha in clouds:
        pygame.draw.circle(
            surface,
            (255, 255, 255, alpha),
            (int(radius + radius * offset_x), int(radius + radius * offset_y)),
            max(6, int(radius * scale)),
        )

    highlight = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
    pygame.draw.circle(
        highlight,
        (255, 255, 255, int(115 * brightness)),
        (radius - radius // 3, radius - radius // 2),
        radius // 2,
    )
    pygame.draw.circle(
        highlight,
        (255, 255, 255, int(42 * brightness)),
        (radius + radius // 4, radius + radius // 3),
        radius // 3,
    )
    surface.blit(highlight, (0, 0))
    pygame.draw.circle(
        surface,
        (255, 255, 255, int(45 * brightness)),
        (radius, radius),
        radius - 4,
        3,
    )
    return surface


def circle_image(image: pygame.Surface, radius: int) -> pygame.Surface:
    size = radius * 2
    scaled_image = pygame.transform.smoothscale(image, (size, size))
    circle = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(circle, (255, 255, 255, 255), (radius, radius), radius)
    circle.blit(scaled_image, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    pygame.draw.circle(circle, (255, 255, 255), (radius, radius), radius, 3)
    return circle
