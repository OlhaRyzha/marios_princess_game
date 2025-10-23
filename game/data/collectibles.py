from dataclasses import dataclass
from typing import Dict, List, Tuple
from game.data.locations import LocationName
from game.utils import GROUND_Y


@dataclass(frozen=True)
class CollectibleSet:
    kind: str
    positions: List[Tuple[int, int]]
    label: str
    hint: str
    image_path: str | None = None
    world_height: int = 72
    icon_height: int = 30


COLLECTIBLE_SETS: Dict[LocationName, CollectibleSet] = {
    "sunny_meadows": CollectibleSet(
        kind="royal_badge",
        positions=[
            (600, GROUND_Y - 280),
            (880, GROUND_Y - 90),
            (1940, GROUND_Y - 260),
        ],
        label="Королівські значки",
        hint="Збери всі королівські значки, щоб відкрити ворота!",
        image_path="assets/blocks/start.png",
        world_height=46,
        icon_height=20,
    ),
    "mushroom_woods": CollectibleSet(
        kind="forest_fruit",
        positions=[
            (940, GROUND_Y - 300),
            (1480, GROUND_Y - 100),
            (2340, GROUND_Y - 260),
        ],
        label="Чарівні фрукти",
        hint="Збери всі фрукти, щоб розбудити лісового боса!",
        image_path="assets/blocks/apple.png",
        world_height=44,
        icon_height=19,
    ),
    "crystal_caves": CollectibleSet(
        kind="crystal_flake",
        positions=[
            (980, GROUND_Y - 320),
            (1620, GROUND_Y - 120),
            (2360, GROUND_Y - 260),
        ],
        label="Кришталеві сніжинки",
        hint="Збери всі сніжинки, щоб матеріалізувати боса!",
    ),
}

__all__ = ["CollectibleSet", "COLLECTIBLE_SETS"]
