from pathlib import Path
from zipfile import BadZipFile, ZipFile

MAX_ARCHIVE_BYTES = 40 * 1024 * 1024


def verify_web_build(archive_path: Path) -> None:
    if not archive_path.is_file():
        raise FileNotFoundError(f"Web archive was not created: {archive_path}")
    if archive_path.stat().st_size > MAX_ARCHIVE_BYTES:
        size_mib = archive_path.stat().st_size / (1024 * 1024)
        raise ValueError(f"Web archive exceeds the 40 MiB budget: {size_mib:.1f} MiB")

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
