from dataclasses import dataclass

from game.data.locations import LocationName
from game.i18n import LocalizedText
from game.utils.constants import GROUND_Y


@dataclass(frozen=True)
class CollectibleSet:
    kind: str
    positions: list[tuple[int, int]]
    label: LocalizedText
    hint: LocalizedText
    image_path: str | None = None
    world_height: int = 72
    icon_height: int = 30


COLLECTIBLE_SETS: dict[LocationName, CollectibleSet] = {
    "sunny_meadows": CollectibleSet(
        kind="royal_badge",
        positions=[
            (600, GROUND_Y - 280),
            (880, GROUND_Y - 90),
            (1940, GROUND_Y - 260),
        ],
        label=LocalizedText("Королівські значки", "Royal Badges"),
        hint=LocalizedText(
            "Збери всі значки, щоб відкрити ворота!",
            "Collect every badge to open the gate!",
        ),
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
        label=LocalizedText("Чарівні фрукти", "Magic Fruit"),
        hint=LocalizedText(
            "Збери всі фрукти, щоб розбудити боса!",
            "Collect every fruit to awaken the boss!",
        ),
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
        label=LocalizedText("Кришталеві сніжинки", "Crystal Flakes"),
        hint=LocalizedText(
            "Збери всі сніжинки, щоб викликати боса!",
            "Collect every flake to reveal the boss!",
        ),
    ),
}
