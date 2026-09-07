from game.ui.objective_card import wrap_text


def test_wrap_text_preserves_words_and_line_limit() -> None:
    text = "Complete previous locations before entering this level"

    lines = wrap_text(text, max_chars=18)

    assert " ".join(lines) == text
    assert all(len(line) <= 18 for line in lines)


def test_wrap_text_returns_no_lines_for_empty_text() -> None:
    assert wrap_text("", max_chars=20) == []
