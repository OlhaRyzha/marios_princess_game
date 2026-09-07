from game.i18n import Language, LocalizedText, Localizer


def test_localizer_uses_ukrainian_by_default_and_toggles_language() -> None:
    localizer = Localizer()
    value = LocalizedText(uk="Перемога", en="Victory")

    assert localizer.resolve(value) == "Перемога"
    assert localizer.toggle() is Language.EN
    assert localizer.resolve(value) == "Victory"


def test_localizer_interpolates_values() -> None:
    localizer = Localizer(Language.EN)

    assert localizer.text("victory.next", location="Crystal Caves") == (
        "Next: Crystal Caves"
    )
