import logging
from pathlib import Path

import pytest

from game.utils.constants import BASE_DIR
from game.utils.images import load_image
from game.utils.paths import resolve_project_path


def test_relative_resource_path_uses_project_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)

    resolved = resolve_project_path("assets/princess/attack/heart.png")

    assert resolved == BASE_DIR / "assets/princess/attack/heart.png"
    assert resolved.is_file()


def test_missing_image_warning_contains_absolute_path(
    pygame_runtime: None,
    caplog: pytest.LogCaptureFixture,
) -> None:
    missing_path = "assets/does-not-exist.png"

    with caplog.at_level(logging.WARNING):
        fallback = load_image(missing_path)

    assert fallback.get_size() == (64, 64)
    assert str(BASE_DIR / missing_path) in caplog.text
