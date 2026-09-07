from pathlib import Path
from zipfile import BadZipFile, ZipFile


def verify_web_build(archive_path: Path) -> None:
    if not archive_path.is_file():
        raise FileNotFoundError(f"Web archive was not created: {archive_path}")

    try:
        with ZipFile(archive_path) as archive:
            names = set(archive.namelist())
    except BadZipFile as error:
        raise ValueError(f"Invalid web archive: {archive_path}") from error

    required_files = {"index.html", "favicon.png", "marios_princess_game.apk"}
    missing_files = required_files - names
    if missing_files:
        missing = ", ".join(sorted(missing_files))
        raise ValueError(f"Web archive is missing required files: {missing}")


if __name__ == "__main__":
    verify_web_build(Path("build/web.zip"))
