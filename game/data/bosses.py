from dataclasses import dataclass
from pathlib import Path

from game.data.locations import LocationName
from game.i18n import LocalizedText
from game.utils.constants import ASSETS_DIR


@dataclass(frozen=True, slots=True)
class BossConfig:
    name: str
    image_path: Path
    about: LocalizedText
    strategy: LocalizedText
    goal: LocalizedText


BOSS_ROSTER: dict[LocationName, tuple[BossConfig, ...]] = {
    "sunny_meadows": (
        BossConfig(
            name="WOODEN THWOMP",
            image_path=ASSETS_DIR / "monsters/wooden_thwomp/wooden_thwomp_1.png",
            about=LocalizedText("Дерев’яний плит-блок.", "A heavy wooden slab."),
            strategy=LocalizedText("Атакуй Heartburst.", "Attack with Heartburst."),
            goal=LocalizedText("Здолай WOODEN THWOMP.", "Defeat WOODEN THWOMP."),
        ),
        BossConfig(
            name="MAD TREE",
            image_path=ASSETS_DIR / "monsters/tree/tree_1.png",
            about=LocalizedText(
                "Злий ент, що кидає шишки.", "An angry ent that throws pine cones."
            ),
            strategy=LocalizedText("Атакуй Heartburst.", "Attack with Heartburst."),
            goal=LocalizedText("Здолай MAD TREE.", "Defeat MAD TREE."),
        ),
    ),
    "mushroom_woods": (
        BossConfig(
            name="FUNGUS TROLL",
            image_path=ASSETS_DIR / "monsters/fungus_troll/fungus_troll_1.png",
            about=LocalizedText("Велетень-гриб.", "A giant mushroom creature."),
            strategy=LocalizedText("Атакуй Heartburst.", "Attack with Heartburst."),
            goal=LocalizedText("Здолай FUNGUS TROLL.", "Defeat FUNGUS TROLL."),
        ),
        BossConfig(
            name="MUSHROOM BRUTE",
            image_path=ASSETS_DIR / "monsters/mushrooms/mushroom_02.png",
            about=LocalizedText("Жвавий гриб.", "A fast and restless mushroom."),
            strategy=LocalizedText("Атакуй Heartburst.", "Attack with Heartburst."),
            goal=LocalizedText("Здолай MUSHROOM BRUTE.", "Defeat MUSHROOM BRUTE."),
        ),
    ),
    "crystal_caves": (
        BossConfig(
            name="GOLEM GEODE",
            image_path=ASSETS_DIR / "monsters/golem_geode/golem_geode_1.png",
            about=LocalizedText(
                "Броньований кристальний голем.", "An armored crystal golem."
            ),
            strategy=LocalizedText("Атакуй Heartburst.", "Attack with Heartburst."),
            goal=LocalizedText("Здолай GOLEM GEODE.", "Defeat GOLEM GEODE."),
        ),
        BossConfig(
            name="CRYSTAL BATS",
            image_path=ASSETS_DIR / "monsters/bats/bat_2.png",
            about=LocalizedText("Величезний кажан.", "A gigantic crystal bat."),
            strategy=LocalizedText("Атакуй Heartburst.", "Attack with Heartburst."),
            goal=LocalizedText("Здолай CRYSTAL BATS.", "Defeat CRYSTAL BATS."),
        ),
    ),
}
