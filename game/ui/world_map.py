import math
import os
import random
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import cast

import pygame

from game.actions import MapAction, MapEvent
from game.data.locations import LOCATION_ORDER, LocationName
from game.data.objectives import ObjectiveConfig
from game.i18n import Localizer
from game.systems.time_source import TimeSource
from game.ui.objective_card import ObjectiveCard
from game.ui.world_map_visuals import circle_image, make_bubble_surface
from game.utils.constants import (
    ASSETS_DIR,
    BACKGROUNDS_DIR,
    FONT_SIZE,
    HEIGHT,
    MAP_DIR,
    WIDTH,
)
from game.utils.fonts import load_font
from game.utils.images import load_image, scale_to_height
from game.utils.paths import resolve_project_path

LocationTitlePair = tuple[LocationName, str]

LOCATIONS: list[LocationTitlePair] = [
    ("sunny_meadows", "Sunny Meadows"),
    ("mushroom_woods", "Mushroom Woods"),
    ("crystal_caves", "Crystal Caves"),
]

LOC_POS: dict[LocationName, tuple[int, int]] = {
    "sunny_meadows": (int(WIDTH * 0.25), int(HEIGHT * 0.55)),
    "mushroom_woods": (int(WIDTH * 0.50), int(HEIGHT * 0.40)),
    "crystal_caves": (int(WIDTH * 0.78), int(HEIGHT * 0.58)),
}

NODE_RADIUS = 64
NODE_DIAMETER = NODE_RADIUS * 2
NODE_HALO = 18
BOSS_THUMB_RADIUS = 38
FOG_PARTICLE_COUNT = 14
FOG_RADIUS_MARGIN = 6

BUBBLE_PALETTES: dict[str, tuple[tuple[int, int, int], tuple[int, int, int]]] = {
    "idle": ((188, 205, 245), (235, 244, 255)),
    "selected": ((205, 215, 255), (248, 252, 255)),
    "completed": ((210, 198, 170), (255, 240, 210)),
    "locked": ((140, 150, 170), (188, 198, 215)),
}

FOG_INTENSITY: dict[str, float] = {
    "selected": 1.15,
    "completed": 0.95,
    "idle": 0.78,
    "locked": 0.55,
}


FALLBACK_BG = os.path.join(BACKGROUNDS_DIR, "mushroom_woods", "sky.png")
MAP_IMAGE = os.path.join(MAP_DIR, "map.png")

MARIO_DIR = os.path.join(ASSETS_DIR, "mario")
MARIO_FILES = [
    "greeting.png",
    "run.png",
    "jump.png",
    "happy.png",
    "ok.png",
]
MARIO_FRAME_MS = 140
MARIO_TARGET_HEIGHT = 120


@dataclass(frozen=True)
class FogParticle:
    base_angle: float
    radius_factor: float
    speed: float
    wobble: float
    size: int
    phase: float


def _load_bg() -> pygame.Surface:
    for path in (MAP_IMAGE, FALLBACK_BG):
        if os.path.exists(path):
            img = load_image(path, convert_alpha=False)
            return pygame.transform.smoothscale(img, (WIDTH, HEIGHT))

    surf = pygame.Surface((WIDTH, HEIGHT))
    surf.fill((140, 160, 220))
    return surf


def _load_image(path: str | Path | None) -> pygame.Surface | None:
    if not path:
        return None
    resolved_path = resolve_project_path(path)
    try:
        if resolved_path.is_file():
            img = pygame.image.load(resolved_path).convert_alpha()
            return img
    except (OSError, pygame.error):
        pass
    return None


def _load_mario_frames(
    target_height: int = MARIO_TARGET_HEIGHT,
) -> list[pygame.Surface]:
    frames: list[pygame.Surface] = []
    if not os.path.isdir(MARIO_DIR):
        return frames
    for name in MARIO_FILES:
        path = os.path.join(MARIO_DIR, name)
        if not os.path.exists(path):
            continue
        img = load_image(path)
        if target_height:
            frames.append(scale_to_height(img, target_height))
        else:
            frames.append(img)
    return frames


class WorldMapScene:

    def __init__(
        self,
        *,
        objectives: Mapping[LocationName, ObjectiveConfig] | None = None,
        boss_thumbs: Mapping[str, str | Path | None] | None = None,
        unlocked: Iterable[LocationName] | None = None,
        completed: Iterable[LocationName] | None = None,
        time_source: TimeSource,
        rng: random.Random,
        localizer: Localizer | None = None,
    ) -> None:
        self.time_source = time_source
        self.rng = rng
        self.localizer = localizer or Localizer()
        self.bg = _load_bg()

        self.font_title = load_font(int(FONT_SIZE * 2.0))
        self.font_label = load_font(int(FONT_SIZE * 0.95))
        self.font_hint = load_font(int(FONT_SIZE * 0.9))
        self.font_card = load_font(int(FONT_SIZE * 0.8))

        self.mario_frames: list[pygame.Surface] = _load_mario_frames()
        self._mario_frame_ms: int = MARIO_FRAME_MS
        self._mario_shadow: pygame.Surface | None = self._make_mario_shadow()
        self._mario_location: LocationName | None = None

        self.objectives: dict[LocationName, ObjectiveConfig] = (
            dict(objectives) if objectives else {}
        )
        self.objective_card = ObjectiveCard(
            font=self.font_card,
            objectives=self.objectives,
            localizer=self.localizer,
        )

        self.boss_thumbs_paths: dict[str, str | Path | None] = (
            dict(boss_thumbs) if boss_thumbs else {}
        )

        self.boss_thumbs_img: dict[str, pygame.Surface | None] = {
            loc: _load_image(self.boss_thumbs_paths.get(loc)) for loc, _ in LOCATIONS
        }

        self.locations: list[LocationName] = [loc for loc, _ in LOCATIONS]
        self.loc_titles: dict[LocationName, str] = {
            loc: title for loc, title in LOCATIONS
        }
        self.selected_idx = 0

        self.completed: set[LocationName] = set(completed) if completed else set()
        self.unlocked: set[LocationName] = set(unlocked) if unlocked else set()
        if not self.unlocked and self.locations:
            self.unlocked.add(self.locations[0])

        self.node_rects: dict[LocationName, pygame.Rect] = {}
        self._rebuild_node_rects()

        self._bubble_surfaces: dict[str, pygame.Surface] = self._build_bubble_surfaces()
        self._fog_particles: dict[LocationName, list[FogParticle]] = (
            self._build_fog_particles()
        )

        self._ensure_selection_focus()
        self._update_mario_location()

    def _build_bubble_surfaces(self) -> dict[str, pygame.Surface]:
        return {
            "idle": make_bubble_surface(
                NODE_RADIUS, BUBBLE_PALETTES["idle"], brightness=1.0
            ),
            "selected": make_bubble_surface(
                NODE_RADIUS, BUBBLE_PALETTES["selected"], brightness=1.12
            ),
            "completed": make_bubble_surface(
                NODE_RADIUS, BUBBLE_PALETTES["completed"], brightness=1.05
            ),
            "locked": make_bubble_surface(
                NODE_RADIUS, BUBBLE_PALETTES["locked"], brightness=0.9
            ),
        }

    def _build_fog_particles(self) -> dict[LocationName, list[FogParticle]]:
        particles: dict[LocationName, list[FogParticle]] = {}
        for loc in self.locations:
            nodes = [
                FogParticle(
                    base_angle=self.rng.uniform(0.0, math.tau),
                    radius_factor=self.rng.uniform(0.2, 0.9),
                    speed=self.rng.uniform(0.45, 0.85),
                    wobble=self.rng.uniform(0.55, 0.95),
                    size=self.rng.randint(3, 7),
                    phase=self.rng.uniform(0.0, math.tau),
                )
                for _ in range(FOG_PARTICLE_COUNT)
            ]
            particles[loc] = nodes
        return particles

    def _rebuild_node_rects(self) -> None:
        self.node_rects.clear()
        for loc in self.locations:
            x, y = LOC_POS[loc]
            r = pygame.Rect(0, 0, NODE_DIAMETER, NODE_DIAMETER)
            r.center = (x, y)
            self.node_rects[loc] = r

    def _make_mario_shadow(self) -> pygame.Surface | None:
        if not self.mario_frames:
            return None
        width = max(frame.get_width() for frame in self.mario_frames)
        surf = pygame.Surface((max(48, int(width * 0.6)), 32), pygame.SRCALPHA)
        pygame.draw.ellipse(
            surf,
            (0, 0, 0, 70),
            (0, surf.get_height() // 3, surf.get_width(), surf.get_height() // 2),
        )
        return surf

    def _current_mario_pos(self) -> tuple[int, int] | None:
        if self._mario_location is None:
            return None
        anchor = LOC_POS.get(self._mario_location)
        if anchor is None:
            return None
        ax, ay = anchor
        return (ax, ay - NODE_RADIUS - 12)

    def _update_mario_location(self) -> None:
        if not self.locations:
            self._mario_location = None
            return
        ordered: list[LocationName] = [
            loc for loc in LOCATION_ORDER if loc in self.locations
        ]
        if not ordered:
            ordered = list(self.locations)
        for loc in reversed(ordered):
            if loc in self.completed:
                self._mario_location = cast(LocationName, loc)
                return
        for loc in ordered:
            if loc in self.unlocked:
                self._mario_location = cast(LocationName, loc)
                return
        self._mario_location = ordered[0]

    def _loc_under_mouse(self, pos: tuple[int, int]) -> LocationName | None:
        for loc, rect in self.node_rects.items():
            if rect.collidepoint(pos):
                cx, cy = rect.center
                dx, dy = pos[0] - cx, pos[1] - cy
                if (dx * dx + dy * dy) <= (NODE_RADIUS * NODE_RADIUS):
                    return loc
        return None

    def _bubble_state(self, loc: LocationName, selected: bool) -> str:
        if loc not in self.unlocked:
            return "locked"
        if selected:
            return "selected"
        if loc in self.completed:
            return "completed"
        return "idle"

    def _draw_fog_overlay(
        self,
        surface: pygame.Surface,
        loc: LocationName,
        center: tuple[int, int],
        intensity: float,
    ) -> None:
        particles = self._fog_particles.get(loc)
        if not particles:
            return

        fog_surface = pygame.Surface((NODE_DIAMETER, NODE_DIAMETER), pygame.SRCALPHA)
        now = self.time_source.now_ms() / 1000.0
        max_r_sq = (NODE_RADIUS - FOG_RADIUS_MARGIN) ** 2

        for particle in particles:
            angle = particle.base_angle + now * particle.speed
            wobble_phase = now * 0.45 + particle.phase
            orbit = particle.radius_factor * (NODE_RADIUS - FOG_RADIUS_MARGIN)
            px = NODE_RADIUS + math.cos(angle) * orbit
            py = (
                NODE_RADIUS
                + math.sin(angle * particle.wobble + wobble_phase) * orbit * 0.86
            )
            dx = px - NODE_RADIUS
            dy = py - NODE_RADIUS
            if dx * dx + dy * dy > max_r_sq:
                continue
            pulse = 0.55 + 0.45 * math.sin(angle * 1.7 + wobble_phase)
            alpha = int(30 + 140 * intensity * pulse)
            alpha = max(18, min(190, alpha))
            pygame.draw.circle(
                fog_surface,
                (255, 255, 255, alpha),
                (int(round(px)), int(round(py))),
                particle.size,
            )

        surface.blit(fog_surface, fog_surface.get_rect(center=center))

    def handle_event(self, e: pygame.event.Event) -> MapEvent | None:

        if e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_LEFT, pygame.K_a):
                self.selected_idx = (self.selected_idx - 1) % len(self.locations)
            elif e.key in (pygame.K_RIGHT, pygame.K_d):
                self.selected_idx = (self.selected_idx + 1) % len(self.locations)
            elif e.key in (pygame.K_UP, pygame.K_w):
                self.selected_idx = (self.selected_idx - 1) % len(self.locations)
            elif e.key in (pygame.K_DOWN, pygame.K_s):
                self.selected_idx = (self.selected_idx + 1) % len(self.locations)
            elif e.key == pygame.K_RETURN:
                loc = self.locations[self.selected_idx]
                if loc in self.unlocked:
                    return MapEvent(MapAction.START, loc)
                return None
            elif e.key == pygame.K_ESCAPE:
                return MapEvent(MapAction.BACK)

        elif e.type == pygame.MOUSEMOTION:
            loc = self._loc_under_mouse(e.pos)
            if loc is not None:
                self.selected_idx = self.locations.index(loc)

        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            loc = self._loc_under_mouse(e.pos)
            if loc is not None:
                self.selected_idx = self.locations.index(loc)
                if loc in self.unlocked:
                    return MapEvent(MapAction.START, loc)

        return None

    def _draw_links(self, surface: pygame.Surface) -> None:

        if len(self.locations) < 2:
            return

        centers = [pygame.math.Vector2(LOC_POS[loc]) for loc in self.locations]
        for start, end in zip(centers, centers[1:], strict=False):
            delta = end - start
            length = delta.length()
            if length <= NODE_RADIUS * 2:
                continue
            direction = delta.normalize()
            start_point = start + direction * NODE_RADIUS
            end_point = end - direction * NODE_RADIUS
            pygame.draw.line(surface, (255, 255, 255), start_point, end_point, 2)
            pygame.draw.aaline(surface, (255, 200, 240), start_point, end_point)

    def _draw_node(
        self, surface: pygame.Surface, loc: LocationName, selected: bool
    ) -> None:
        cx, cy = LOC_POS[loc]
        unlocked = loc in self.unlocked
        completed = loc in self.completed

        if selected:
            halo = pygame.Surface((NODE_RADIUS * 4, NODE_RADIUS * 4), pygame.SRCALPHA)
            halo_color = (255, 220, 250, 90) if unlocked else (200, 210, 230, 70)
            pygame.draw.circle(
                halo,
                halo_color,
                (halo.get_width() // 2, halo.get_height() // 2),
                NODE_RADIUS + NODE_HALO,
            )
            surface.blit(
                halo, (cx - halo.get_width() // 2, cy - halo.get_height() // 2)
            )

        state = self._bubble_state(loc, selected)
        bubble_surface = self._bubble_surfaces[state]
        surface.blit(bubble_surface, bubble_surface.get_rect(center=(cx, cy)))

        intensity = FOG_INTENSITY.get(state, 0.75)
        if selected and state != "locked":
            intensity += 0.1
        self._draw_fog_overlay(surface, loc, (cx, cy), intensity)

        pygame.draw.circle(surface, (255, 255, 255), (cx, cy), NODE_RADIUS, 4)
        pygame.draw.circle(surface, (255, 245, 252), (cx, cy), NODE_RADIUS - 3, 2)

        if selected:
            img = self.boss_thumbs_img.get(loc)
            if img:
                icon = circle_image(img, BOSS_THUMB_RADIUS)
                surface.blit(
                    icon, (cx - icon.get_width() // 2, cy - icon.get_height() // 2)
                )

        if not unlocked:
            mask = pygame.Surface((NODE_DIAMETER, NODE_DIAMETER), pygame.SRCALPHA)
            pygame.draw.circle(
                mask,
                (25, 25, 35, 150),
                (NODE_RADIUS, NODE_RADIUS),
                NODE_RADIUS,
            )
            surface.blit(mask, mask.get_rect(center=(cx, cy)))

        label = self.loc_titles.get(loc, loc)
        label_color = (255, 255, 255) if unlocked else (170, 170, 175)
        label_surf = self.font_label.render(label, True, label_color)
        lx = cx - label_surf.get_width() // 2
        ly = cy + NODE_RADIUS + 12
        surface.blit(label_surf, (lx, ly))

        if completed:
            badge = pygame.Surface((28, 28), pygame.SRCALPHA)
            pygame.draw.circle(badge, (40, 170, 110), (14, 14), 14)
            pygame.draw.lines(
                badge, (255, 255, 255), False, [(7, 15), (12, 20), (20, 8)], 3
            )
            surface.blit(
                badge,
                badge.get_rect(center=(cx + NODE_RADIUS - 14, cy - NODE_RADIUS + 14)),
            )

    def _draw_mario(self, surface: pygame.Surface) -> None:
        if not self.mario_frames or not self.completed:
            return
        pos = self._current_mario_pos()
        if pos is None:
            return
        now = self.time_source.now_ms()
        frame_idx = (now // self._mario_frame_ms) % len(self.mario_frames)
        frame = self.mario_frames[frame_idx]
        bob = int(3 * math.sin(now / 260.0))
        draw_y = pos[1] + bob
        if self._mario_shadow:
            shadow_rect = self._mario_shadow.get_rect(center=(pos[0], pos[1] + 22))
            surface.blit(self._mario_shadow, shadow_rect)
        surface.blit(frame, frame.get_rect(midbottom=(pos[0], draw_y)))

    def draw(self, surface: pygame.Surface, *, overlay: bool) -> None:

        surface.blit(self.bg, (0, 0))

        if overlay:
            dim = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            dim.fill((0, 0, 0, 90))
            surface.blit(dim, (0, 0))

        self._draw_links(surface)

        for i, loc in enumerate(self.locations):
            self._draw_node(surface, loc, selected=(i == self.selected_idx))

        self._draw_mario(surface)

        location = self.locations[self.selected_idx]
        self.objective_card.draw(
            surface,
            location,
            locked=location not in self.unlocked,
        )

    def set_progress(
        self, *, unlocked: Iterable[LocationName], completed: Iterable[LocationName]
    ) -> None:
        self.completed = set(completed)
        self.unlocked = set(unlocked)
        if not self.unlocked and self.locations:
            self.unlocked.add(self.locations[0])
        self._ensure_selection_focus()
        self._update_mario_location()

    def _ensure_selection_focus(self) -> None:
        if not self.locations:
            self.selected_idx = 0
            return
        self.selected_idx = max(0, min(self.selected_idx, len(self.locations) - 1))
        current = self.locations[self.selected_idx]
        if current in self.unlocked:
            return
        for idx, loc in enumerate(self.locations):
            if loc in self.unlocked:
                self.selected_idx = idx
                return
