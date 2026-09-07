from dataclasses import dataclass
from pathlib import Path

from game.data.locations import LocationName
from game.utils.constants import ASSETS_DIR


@dataclass(frozen=True, slots=True)
class BossConfig:
    name: str
    image_path: Path
    about: str
    strategy: str
    goal: str


BOSS_ROSTER: dict[LocationName, tuple[BossConfig, ...]] = {
    "sunny_meadows": (
        BossConfig(
            name="WOODEN THWOMP",
            image_path=ASSETS_DIR / "monsters/wooden_thwomp/wooden_thwomp_1.png",
            about="Дерев’яний плит-блок.",
            strategy="Бий Heartburst.",
            goal="Перемогти WOODEN THWOMP та перейти на інший рівень.",
        ),
        BossConfig(
            name="MAD TREE",
            image_path=ASSETS_DIR / "monsters/tree/tree_1.png",
            about="Злий ент, б’є гіллям і викидає шишки.",
            strategy="Бий Heartburst.",
            goal="Перемогти MAD TREE та перейти на інший рівень.",
        ),
    ),
    "mushroom_woods": (
        BossConfig(
            name="FUNGUS TROLL",
            image_path=ASSETS_DIR / "monsters/fungus_troll/fungus_troll_1.png",
            about="Велет-гриб",
            strategy="Бий Heartburst.",
            goal="Перемогти FUNGUS TROLL та перейти на інший рівень.",
        ),
        BossConfig(
            name="MUSHROOM BRUTE",
            image_path=ASSETS_DIR / "monsters/mushrooms/mushroom_02.png",
            about="Жвавий гриб.",
            strategy="Бий Heartburst.",
            goal="Перемогти MUSHROOM BRUTE та перейти на інший рівень.",
        ),
    ),
    "crystal_caves": (
        BossConfig(
            name="GOLEM GEODE",
            image_path=ASSETS_DIR / "monsters/golem_geode/golem_geode_1.png",
            about="Кристальний голем з бронею.",
            strategy="Бий Heartburst.",
            goal="Перемогти GOLEM GEODE та врятувати Маріо.",
        ),
        BossConfig(
            name="CRYSTAL BATS",
            image_path=ASSETS_DIR / "monsters/bats/bat_2.png",
            about="Величезний кажан.",
            strategy="Бий Heartburst.",
            goal="Перемогти CRYSTAL BATS та врятувати Маріо.",
        ),
    ),
}
