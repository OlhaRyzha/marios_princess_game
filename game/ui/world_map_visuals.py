import pygame


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
