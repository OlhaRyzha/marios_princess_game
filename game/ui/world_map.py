import os
import random
from collections.abc import Iterable, Mapping
from pathlib import Path

import pygame

from game.actions import MapAction, MapEvent
from game.data.locations import LocationName
from game.data.objectives import ObjectiveConfig
from game.i18n import Localizer
from game.systems.time_source import TimeSource
from game.ui.objective_card import ObjectiveCard
from game.ui.world_map_renderer import WorldMapRenderer
from game.ui.world_map_state import WorldMapState
from game.ui.world_map_visuals import MapFog, make_bubble_surface
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


def _load_bg() -> "pygame.Surface":
    for path in (MAP_IMAGE, FALLBACK_BG):
        if os.path.exists(path):
            img = load_image(path, convert_alpha=False)
            return pygame.transform.smoothscale(img, (WIDTH, HEIGHT))

    surf = pygame.Surface((WIDTH, HEIGHT))
    surf.fill((140, 160, 220))
    return surf


def _load_image(path: str | Path | None) -> "pygame.Surface | None":
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
) -> "list[pygame.Surface]":
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

        locations: list[LocationName] = [loc for loc, _ in LOCATIONS]
        self.loc_titles: dict[LocationName, str] = {
            loc: title for loc, title in LOCATIONS
        }
        self.state = WorldMapState(
            locations,
            set(unlocked) if unlocked else set(),
            set(completed) if completed else set(),
        )

        self.node_rects: dict[LocationName, pygame.Rect] = {}
        self._rebuild_node_rects()

        self._bubble_surfaces: dict[str, pygame.Surface] = self._build_bubble_surfaces()
        self.fog = MapFog(
            locations=self.locations,
            rng=self.rng,
            time_source=self.time_source,
            radius=NODE_RADIUS,
        )
        self.renderer = WorldMapRenderer(
            positions=LOC_POS,
            node_radius=NODE_RADIUS,
            node_halo=NODE_HALO,
            boss_thumb_radius=BOSS_THUMB_RADIUS,
            fog_intensity=FOG_INTENSITY,
        )

    @property
    def locations(self) -> list[LocationName]:
        return self.state.locations

    @property
    def selected_idx(self) -> int:
        return self.state.selected_index

    @selected_idx.setter
    def selected_idx(self, value: int) -> None:
        self.state.selected_index = value

    @property
    def completed(self) -> set[LocationName]:
        return self.state.completed

    @property
    def unlocked(self) -> set[LocationName]:
        return self.state.unlocked

    def _build_bubble_surfaces(self) -> "dict[str, pygame.Surface]":
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

    def _rebuild_node_rects(self) -> None:
        self.node_rects.clear()
        for loc in self.locations:
            x, y = LOC_POS[loc]
            r = pygame.Rect(0, 0, NODE_DIAMETER, NODE_DIAMETER)
            r.center = (x, y)
            self.node_rects[loc] = r

    def _make_mario_shadow(self) -> "pygame.Surface | None":
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

    def _loc_under_mouse(self, pos: tuple[int, int]) -> LocationName | None:
        for loc, rect in self.node_rects.items():
            if rect.collidepoint(pos):
                cx, cy = rect.center
                dx, dy = pos[0] - cx, pos[1] - cy
                if (dx * dx + dy * dy) <= (NODE_RADIUS * NODE_RADIUS):
                    return loc
        return None

    def handle_event(self, e: "pygame.event.Event") -> MapEvent | None:

        if e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_LEFT, pygame.K_a):
                self.state.move(-1)
            elif e.key in (pygame.K_RIGHT, pygame.K_d):
                self.state.move(1)
            elif e.key in (pygame.K_UP, pygame.K_w):
                self.state.move(-1)
            elif e.key in (pygame.K_DOWN, pygame.K_s):
                self.state.move(1)
            elif e.key == pygame.K_RETURN:
                loc = self.locations[self.selected_idx]
                if loc in self.unlocked:
                    return MapEvent(MapAction.START, loc)
                return None
            elif e.key == pygame.K_ESCAPE:
                return MapEvent(MapAction.BACK)

        elif e.type == pygame.MOUSEMOTION:
            hovered_location = self._loc_under_mouse(e.pos)
            if hovered_location is not None:
                self.state.select(hovered_location)

        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            clicked_location = self._loc_under_mouse(e.pos)
            if clicked_location is not None:
                self.state.select(clicked_location)
                if clicked_location in self.unlocked:
                    return MapEvent(MapAction.START, clicked_location)

        return None

    def draw(self, surface: "pygame.Surface", *, overlay: bool) -> None:
        self.renderer.draw(surface, self, overlay=overlay)

    def set_progress(
        self, *, unlocked: Iterable[LocationName], completed: Iterable[LocationName]
    ) -> None:
        self.state.set_progress(unlocked=unlocked, completed=completed)
