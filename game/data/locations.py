from __future__ import annotations

from typing import Dict, Literal

from game.utils import TARGET_H, CROUCH_SCALE

LocationName = Literal["sunny_meadows", "mushroom_woods", "crystal_caves"]

LOCATION_ORDER: list[LocationName] = [
    "sunny_meadows",
    "mushroom_woods",
    "crystal_caves",
]


def crawl_gap() -> int:
    return int(TARGET_H * CROUCH_SCALE) + 8


MEADOWS_PATTERN = [
    ("WOODEN_PLATFORM_MOVING", "ground", 0),
    ("BUSH_SPRING", "ground", 0),
    ("FRAGILE_BLOCK", "air", "crawl"),
    ("PIT_HOLE", "ground", 0),
]
WOODS_PATTERN = [
    ("MUSHROOM_BOUNCE", "ground", 0),
    ("POISON_POOL", "ground", 0),
    ("ONE_WAY_PLATFORM", "air", "crawl"),
    ("VINE_CLIMB", "ground", 0),
]
CAVES_PATTERN = [
    ("ICE_TILE", "ground", 0),
    ("CRYSTAL_BRIDGE", "air", "crawl"),
    ("STALACTITE_FALL", "air", 180),
    ("MINECART_RAIL", "ground", 0),
]

NEXT_LOCATION: Dict[LocationName, LocationName | None] = {
    "sunny_meadows": "mushroom_woods",
    "mushroom_woods": "crystal_caves",
    "crystal_caves": None,
}

__all__ = [
    "LocationName",
    "LOCATION_ORDER",
    "crawl_gap",
    "MEADOWS_PATTERN",
    "WOODS_PATTERN",
    "CAVES_PATTERN",
    "NEXT_LOCATION",
]
