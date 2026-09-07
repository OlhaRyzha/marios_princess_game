from dataclasses import dataclass

from game.data.locations import LocationName
from game.i18n import LocalizedText, Localizer


@dataclass(frozen=True, slots=True)
class ObjectiveConfig:
    title: str
    description: tuple[LocalizedText, ...]
    boss_hints: tuple[LocalizedText, ...]

    def lines(self, localizer: Localizer) -> tuple[str, ...]:
        return tuple(
            localizer.resolve(line) for line in self.description + self.boss_hints
        )


OBJECTIVES: dict[LocationName, ObjectiveConfig] = {
    "sunny_meadows": ObjectiveConfig(
        title="Sunny Meadows",
        description=(
            LocalizedText(
                "Остерігайся ям і хитких платформ.",
                "Watch for pits and unstable platforms.",
            ),
            LocalizedText("Збери 3 Королівські значки.", "Collect 3 Royal Badges."),
            LocalizedText(
                "Дістанься воріт у грибний ліс.", "Reach the gate to Mushroom Woods."
            ),
        ),
        boss_hints=(
            LocalizedText(
                "Wooden Thwomp вразливий після удару об землю.",
                "Wooden Thwomp is vulnerable after hitting the ground.",
            ),
        ),
    ),
    "mushroom_woods": ObjectiveConfig(
        title="Mushroom Woods",
        description=(
            LocalizedText("Остерігайся отруйних калюж.", "Avoid the poisonous pools."),
            LocalizedText("Збери всі чарівні фрукти.", "Collect every Magic Fruit."),
            LocalizedText(
                "Знайди шлях до кришталевих печер.", "Find the route to Crystal Caves."
            ),
        ),
        boss_hints=(
            LocalizedText(
                "Стрибай через хвилі Fungus Troll.",
                "Jump over the waves created by Fungus Troll.",
            ),
        ),
    ),
    "crystal_caves": ObjectiveConfig(
        title="Crystal Caves",
        description=(
            LocalizedText(
                "Остерігайся льоду та сталактитів.",
                "Watch for ice and falling stalactites.",
            ),
            LocalizedText(
                "Збери всі кришталеві сніжинки.", "Collect every Crystal Flake."
            ),
            LocalizedText(
                "Знайди Маріо в серці печер.", "Find Mario in the heart of the caves."
            ),
        ),
        boss_hints=(
            LocalizedText(
                "Здолай Golem Geode і Crystal Bats.",
                "Defeat Golem Geode and Crystal Bats.",
            ),
        ),
    ),
}


CONTROLS: tuple[LocalizedText, ...] = (
    LocalizedText("РУХ: ←/→", "MOVE: ←/→"),
    LocalizedText("СТРИБОК: Space", "JUMP: Space"),
    LocalizedText("ПРИСІСТИ: ↓", "CROUCH: ↓"),
    LocalizedText("АТАКА Heartburst: J", "HEARTBURST: J"),
    LocalizedText("ПАУЗА/НАЗАД: Esc", "PAUSE/BACK: Esc"),
    LocalizedText("МОВА: L", "LANGUAGE: L"),
)
