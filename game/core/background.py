import os
from typing import Literal, TypedDict, cast

import pygame

from game.utils.constants import (
    BACKGROUNDS_DIR,
    GROUND_STRIP_H,
    GROUND_THEMES,
    GROUND_Y,
    HEIGHT,
    PARALLAX_LAYOUT,
    PARALLAX_PRESETS,
    WIDTH,
)
from game.utils.images import load_image


class LayerPreset(TypedDict):
    speed: float


class LocationPreset(TypedDict):
    far: LayerPreset
    mid: LayerPreset
    fore: LayerPreset


class LayerLayout(TypedDict, total=False):
    target_h: int
    above: int
    tile: Literal["repeat", "mirror"]
    show_top: int | None


class LocationLayout(TypedDict):
    far: LayerLayout
    mid: LayerLayout
    fore: LayerLayout


def _scale_to_height(img: "pygame.Surface", target_h: int | None) -> "pygame.Surface":
    if not target_h:
        return img
    w, h = img.get_size()
    if h <= 0:
        return img
    k = target_h / h
    return pygame.transform.smoothscale(img, (int(w * k), int(h * k)))


class ParallaxBackground:
    def __init__(self, location: str = "sunny_meadows"):
        self.set_location(location)

    def set_location(self, location: str):
        presets = cast(dict[str, LocationPreset], PARALLAX_PRESETS)
        layouts = cast(dict[str, LocationLayout], PARALLAX_LAYOUT)
        if location not in presets or location not in layouts:
            location = "sunny_meadows"
        self.location = location
        loc_dir = os.path.join(BACKGROUNDS_DIR, location)

        self.sky = load_image(os.path.join(loc_dir, "sky.jpg"))
        far_raw = load_image(os.path.join(loc_dir, "far.png"))
        mid_raw = load_image(os.path.join(loc_dir, "mid.png"))
        fore_raw = load_image(os.path.join(loc_dir, "fore.png"))

        layout = layouts[location]
        self.l_far: LayerLayout = layout["far"]
        self.l_mid: LayerLayout = layout["mid"]
        self.l_fore: LayerLayout = layout["fore"]

        far_target = self.l_far.get("target_h")
        mid_target = self.l_mid.get("target_h")
        fore_target = self.l_fore.get("target_h")

        self.far = _scale_to_height(far_raw, far_target)
        self.mid = _scale_to_height(mid_raw, mid_target)
        self.fore = _scale_to_height(fore_raw, fore_target)

        self.cfg: LocationPreset = presets[location]

    def draw(self, surface: "pygame.Surface", cam_x: float) -> None:

        surface.blit(pygame.transform.smoothscale(self.sky, (WIDTH, HEIGHT)), (0, 0))

        self._blit_tiled(
            surface,
            self.far,
            cam_x,
            speed=self.cfg["far"]["speed"],
            above=self.l_far.get("above", -100),
            tile=self.l_far.get("tile", "repeat"),
            show_top=self.l_far.get("show_top"),
        )

        self._blit_tiled(
            surface,
            self.mid,
            cam_x,
            speed=self.cfg["mid"]["speed"],
            above=self.l_mid.get("above", -40),
            tile=self.l_mid.get("tile", "repeat"),
            show_top=self.l_mid.get("show_top"),
        )

        self._blit_tiled(
            surface,
            self.fore,
            cam_x,
            speed=self.cfg["fore"]["speed"],
            above=self.l_fore.get("above", -40),
            tile=self.l_fore.get("tile", "repeat"),
            show_top=self.l_fore.get("show_top"),
        )

        self._draw_ground(surface)

    def _blit_tiled(
        self,
        surface: "pygame.Surface",
        img: "pygame.Surface",
        cam_x: float,
        *,
        speed: float,
        above: int,
        tile: str = "repeat",
        show_top: int | None = None,
    ) -> None:
        src_h = (
            show_top if (show_top and show_top < img.get_height()) else img.get_height()
        )
        src_rect = pygame.Rect(0, 0, img.get_width(), src_h)

        y = GROUND_Y - src_h - above
        w = img.get_width()
        x = -int(cam_x * speed) % w - w

        flip = False
        while x < surface.get_width():
            if tile == "mirror" and flip:
                flipped = pygame.transform.flip(img, True, False)
                surface.blit(flipped, (x, y), area=src_rect)
            else:
                surface.blit(img, (x, y), area=src_rect)
            x += w
            flip = not flip if tile == "mirror" else False

    def _draw_ground(self, surface: "pygame.Surface") -> None:
        theme = GROUND_THEMES.get(self.location, GROUND_THEMES["sunny_meadows"])
        soil_base = theme["soil_base"]
        grass_top = theme["grass_top"]
        grass_edge = theme["grass_edge"]
        stone_a = theme["stone_a"]
        stone_b = theme["stone_b"]

        y0 = surface.get_height() - GROUND_STRIP_H

        pygame.draw.rect(
            surface, soil_base, (0, y0 + 40, surface.get_width(), GROUND_STRIP_H - 40)
        )
        pygame.draw.rect(surface, grass_top, (0, y0, surface.get_width(), 48))
        pygame.draw.rect(surface, grass_edge, (0, y0 + 44, surface.get_width(), 6))
        for x in range(0, surface.get_width(), 180):
            pygame.draw.ellipse(
                surface, stone_a, (x + 40, y0 + GROUND_STRIP_H - 28, 60, 22)
            )
            pygame.draw.ellipse(
                surface, stone_b, (x + 95, y0 + GROUND_STRIP_H - 22, 36, 14)
            )
