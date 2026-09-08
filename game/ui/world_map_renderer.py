import math
from typing import Protocol

import pygame

from game.data.locations import LocationName
from game.systems.time_source import TimeSource
from game.ui.objective_card import ObjectiveCard
from game.ui.world_map_visuals import MapFog, circle_image
from game.utils.constants import HEIGHT, WIDTH


class WorldMapView(Protocol):
    bg: pygame.Surface
    loc_titles: dict[LocationName, str]
    boss_thumbs_img: dict[str, pygame.Surface | None]
    font_label: pygame.font.Font
    mario_frames: list[pygame.Surface]
    time_source: TimeSource
    objective_card: ObjectiveCard
    fog: MapFog
    _bubble_surfaces: dict[str, pygame.Surface]
    _mario_frame_ms: int
    _mario_shadow: pygame.Surface | None

    @property
    def locations(self) -> list[LocationName]: ...

    @property
    def selected_idx(self) -> int: ...

    @property
    def unlocked(self) -> set[LocationName]: ...

    @property
    def completed(self) -> set[LocationName]: ...


class WorldMapRenderer:
    """Render the world map without handling input or changing progress."""

    def __init__(
        self,
        *,
        positions: dict[LocationName, tuple[int, int]],
        node_radius: int,
        node_halo: int,
        boss_thumb_radius: int,
        fog_intensity: dict[str, float],
    ) -> None:
        self.positions = positions
        self.node_radius = node_radius
        self.node_halo = node_halo
        self.boss_thumb_radius = boss_thumb_radius
        self.fog_intensity = fog_intensity

    def _bubble_state(
        self, scene: WorldMapView, location: LocationName, selected: bool
    ) -> str:
        if location not in scene.unlocked:
            return "locked"
        if selected:
            return "selected"
        if location in scene.completed:
            return "completed"
        return "idle"

    def _draw_links(self, surface: pygame.Surface, scene: WorldMapView) -> None:
        if len(scene.locations) < 2:
            return
        centers = [pygame.Vector2(self.positions[loc]) for loc in scene.locations]
        for start, end in zip(centers, centers[1:], strict=False):
            delta = end - start
            if delta.length() <= self.node_radius * 2:
                continue
            direction = delta.normalize()
            start_point = start + direction * self.node_radius
            end_point = end - direction * self.node_radius
            pygame.draw.line(surface, (255, 255, 255), start_point, end_point, 2)
            pygame.draw.aaline(surface, (255, 200, 240), start_point, end_point)

    def _draw_node(
        self,
        surface: pygame.Surface,
        scene: WorldMapView,
        location: LocationName,
        selected: bool,
    ) -> None:
        center_x, center_y = self.positions[location]
        unlocked = location in scene.unlocked
        completed = location in scene.completed
        if selected:
            halo = pygame.Surface(
                (self.node_radius * 4, self.node_radius * 4), pygame.SRCALPHA
            )
            halo_color = (255, 220, 250, 90) if unlocked else (200, 210, 230, 70)
            pygame.draw.circle(
                halo,
                halo_color,
                (halo.get_width() // 2, halo.get_height() // 2),
                self.node_radius + self.node_halo,
            )
            surface.blit(
                halo,
                (center_x - halo.get_width() // 2, center_y - halo.get_height() // 2),
            )

        state = self._bubble_state(scene, location, selected)
        bubble = scene._bubble_surfaces[state]
        surface.blit(bubble, bubble.get_rect(center=(center_x, center_y)))
        intensity = self.fog_intensity.get(state, 0.75)
        if selected and state != "locked":
            intensity += 0.1
        scene.fog.draw(surface, location, (center_x, center_y), intensity)
        pygame.draw.circle(
            surface, (255, 255, 255), (center_x, center_y), self.node_radius, 4
        )
        pygame.draw.circle(
            surface,
            (255, 245, 252),
            (center_x, center_y),
            self.node_radius - 3,
            2,
        )
        image = scene.boss_thumbs_img.get(location)
        if selected and image:
            icon = circle_image(image, self.boss_thumb_radius)
            surface.blit(
                icon,
                (center_x - icon.get_width() // 2, center_y - icon.get_height() // 2),
            )
        if not unlocked:
            diameter = self.node_radius * 2
            mask = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
            pygame.draw.circle(
                mask,
                (25, 25, 35, 150),
                (self.node_radius, self.node_radius),
                self.node_radius,
            )
            surface.blit(mask, mask.get_rect(center=(center_x, center_y)))
        label = scene.font_label.render(
            scene.loc_titles.get(location, location),
            True,
            (255, 255, 255) if unlocked else (170, 170, 175),
        )
        surface.blit(
            label,
            (
                center_x - label.get_width() // 2,
                center_y + self.node_radius + 12,
            ),
        )
        if completed:
            badge = pygame.Surface((28, 28), pygame.SRCALPHA)
            pygame.draw.circle(badge, (40, 170, 110), (14, 14), 14)
            pygame.draw.lines(
                badge, (255, 255, 255), False, [(7, 15), (12, 20), (20, 8)], 3
            )
            surface.blit(
                badge,
                badge.get_rect(
                    center=(
                        center_x + self.node_radius - 14,
                        center_y - self.node_radius + 14,
                    )
                ),
            )

    def _draw_mario(self, surface: pygame.Surface, scene: WorldMapView) -> None:
        if not scene.mario_frames or not scene.completed:
            return
        mario_location = max(
            scene.completed, key=lambda location: scene.locations.index(location)
        )
        anchor = self.positions[mario_location]
        position = (anchor[0], anchor[1] - self.node_radius - 12)
        now = scene.time_source.now_ms()
        frame = scene.mario_frames[
            (now // scene._mario_frame_ms) % len(scene.mario_frames)
        ]
        draw_y = position[1] + int(3 * math.sin(now / 260.0))
        if scene._mario_shadow:
            shadow_rect = scene._mario_shadow.get_rect(
                center=(position[0], position[1] + 22)
            )
            surface.blit(scene._mario_shadow, shadow_rect)
        surface.blit(frame, frame.get_rect(midbottom=(position[0], draw_y)))

    def draw(
        self, surface: pygame.Surface, scene: WorldMapView, *, overlay: bool
    ) -> None:
        """Draw the complete map and its objective card."""
        surface.blit(scene.bg, (0, 0))
        if overlay:
            dim = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            dim.fill((0, 0, 0, 90))
            surface.blit(dim, (0, 0))
        self._draw_links(surface, scene)
        for index, location in enumerate(scene.locations):
            self._draw_node(
                surface, scene, location, selected=index == scene.selected_idx
            )
        self._draw_mario(surface, scene)
        location = scene.locations[scene.selected_idx]
        scene.objective_card.draw(
            surface, location, locked=location not in scene.unlocked
        )
