from pathlib import Path
from zipfile import ZipFile

import pytest

from scripts.verify_web_build import verify_web_build


def test_verify_web_build_accepts_required_root_files(tmp_path: Path) -> None:
    archive_path = tmp_path / "web.zip"
    with ZipFile(archive_path, "w") as archive:
        archive.writestr(
            "index.html",
            '<script src="https://example.com/app.js"><div class="loading-track">',
        )
        archive.writestr("favicon.png", "content")
        archive.writestr("marios_princess_game.apk", "content")

    verify_web_build(archive_path)


def test_verify_web_build_reports_missing_root_files(tmp_path: Path) -> None:
    archive_path = tmp_path / "web.zip"
    with ZipFile(archive_path, "w") as archive:
        archive.writestr("nested/index.html", "content")

    with pytest.raises(ValueError, match="favicon.png, index.html"):
        verify_web_build(archive_path)


def test_verify_web_build_rejects_localhost_runtime_url(tmp_path: Path) -> None:
    archive_path = tmp_path / "web.zip"
    with ZipFile(archive_path, "w") as archive:
        archive.writestr(
            "index.html",
            '<script src="http://localhost/cdn/app.js"><div class="loading-track">',
        )
        archive.writestr("favicon.png", "content")
        archive.writestr("marios_princess_game.apk", "content")

    with pytest.raises(ValueError, match="localhost runtime URL"):
        verify_web_build(archive_path)


def test_verify_web_build_requires_themed_loading_screen(tmp_path: Path) -> None:
    archive_path = tmp_path / "web.zip"
    with ZipFile(archive_path, "w") as archive:
        archive.writestr("index.html", '<script src="https://example.com/app.js">')
        archive.writestr("favicon.png", "content")
        archive.writestr("marios_princess_game.apk", "content")

    with pytest.raises(ValueError, match="themed loading screen"):
        verify_web_build(archive_path)
