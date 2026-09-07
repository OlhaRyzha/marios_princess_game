from dataclasses import dataclass

from game.data.locations import LocationName


@dataclass(frozen=True, slots=True)
class ObjectiveConfig:
    title: str
    description: tuple[str, ...]
    boss_hints: tuple[str, ...]

    @property
    def lines(self) -> tuple[str, ...]:
        return self.description + self.boss_hints


OBJECTIVES: dict[LocationName, ObjectiveConfig] = {
    "sunny_meadows": ObjectiveConfig(
        title="Sunny Meadows",
        description=(
            "Сонячні луки повні ям і хитких платформ — будь обережна, принцесо!",
            "Збери 3 Королівські значки, сховані між квітами й кущами.",
            "Пройди шлях до воріт, що ведуть у таємничий грибний ліс.",
        ),
        boss_hints=(
            "Міні-бос: Wooden Thwomp — важкий дерев’яний велетень; бий, коли він застряг у землі!",
        ),
    ),
    "mushroom_woods": ObjectiveConfig(
        title="Mushroom Woods",
        description=(
            "Грибний ліс повен таємниць: бережись отруйних калюж і розумних грибів-вимикачів.",
            "Збери всі фрукти, щоб розбудити лісового боса!",
            "У глибині лісу схований шахтний ліфт до кришталевих печер.",
        ),
        boss_hints=(
            "Міні-бос: Fungus Troll — велетень із грибною шапкою; стрибай, коли його тупіт здіймає хвилі!",
        ),
    ),
    "crystal_caves": ObjectiveConfig(
        title="Crystal Caves",
        description=(
            "Кришталеві печери сяють і ковзають — остерігайся сталактитів.",
            "Збери всі сніжинки, щоб матеріалізувати боса!",
            "У самому серці печер чекає Kamek — чаклун призм і тіней.",
        ),
        boss_hints=(
            "Golem Geode — кам’яний велет із сяючими ядрами; відбивай промені Kamek у чарівні призми!",
        ),
    ),
}


CONTROLS: tuple[str, ...] = (
    "РУХ: ←/→",
    "СТРИБОК: Space",
    "ПРИСІСТИ: ↓",
    "АТАКА Heartburst: J",
    "Пауза/назад: Esc",
)
