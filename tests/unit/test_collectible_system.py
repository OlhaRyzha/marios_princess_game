import random

from game.gameplay.collectible_system import CollectibleSystem
from game.i18n import Language, Localizer


def test_collectible_system_loads_and_collects_level_items(
    pygame_runtime: None,
) -> None:
    system = CollectibleSystem(rng=random.Random(2026), localizer=Localizer())
    system.load("sunny_meadows")
    first = next(iter(system.sprites))

    positions = system.collect(first.rect)

    assert positions == [first.rect.center]
    assert system.collected == 1
    assert system.progress == (1, 3)
    assert len(system.sprites) == 2


def test_collectible_labels_follow_selected_language(pygame_runtime: None) -> None:
    localizer = Localizer()
    system = CollectibleSystem(rng=random.Random(2026), localizer=localizer)
    system.load("mushroom_woods")

    assert system.label == "Чарівні фрукти"
    localizer.language = Language.EN
    assert system.label == "Magic Fruit"
