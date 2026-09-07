import pygame

from game.i18n import Language, Localizer
from game.ui.ui_modal import VictoryModal


def test_victory_modal_calls_continue_once(pygame_runtime: None) -> None:
    calls: list[str] = []
    modal = VictoryModal(
        title="Victory",
        lines=["Mario is free."],
        on_continue=lambda: calls.append("continue"),
    )

    modal.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
    modal.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))

    assert not modal.active
    assert calls == ["continue"]


def test_victory_modal_uses_localized_footer(pygame_runtime: None) -> None:
    localizer = Localizer(Language.UK)
    modal = VictoryModal(
        title="Перемога",
        lines=["Маріо вільний."],
        on_continue=None,
        localizer=localizer,
    )

    assert modal.localizer.text("victory.finish") == (
        "Натисни Enter, щоб завершити гру"
    )


def test_victory_modal_wraps_and_limits_long_text() -> None:
    lines = ["one two three four five six seven eight", "second line"]

    wrapped = VictoryModal._wrap_lines(lines, max_chars=8, max_lines=4)

    assert len(wrapped) == 4
    assert wrapped[-1] == "…"
