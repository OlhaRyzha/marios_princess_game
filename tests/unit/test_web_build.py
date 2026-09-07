from pathlib import Path
from zipfile import ZipFile

import pytest

from scripts.verify_web_build import verify_web_build


def test_verify_web_build_accepts_required_root_files(tmp_path: Path) -> None:
    archive_path = tmp_path / "web.zip"
    with ZipFile(archive_path, "w") as archive:
        for name in ("index.html", "favicon.png", "marios_princess_game.apk"):
            archive.writestr(name, "content")

    verify_web_build(archive_path)


def test_verify_web_build_reports_missing_root_files(tmp_path: Path) -> None:
    archive_path = tmp_path / "web.zip"
    with ZipFile(archive_path, "w") as archive:
        archive.writestr("nested/index.html", "content")

    with pytest.raises(ValueError, match="favicon.png, index.html"):
        verify_web_build(archive_path)
