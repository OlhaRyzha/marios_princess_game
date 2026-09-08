from pathlib import Path

ASSET_DIRECTORY = Path("assets")
MAX_FILE_BYTES = 10 * 1024 * 1024
MAX_TOTAL_BYTES = 35 * 1024 * 1024
ALLOWED_JPEG_FILES = {
    Path("assets/backgrounds/crystal_caves/sky.jpg"),
    Path("assets/backgrounds/mushroom_woods/sky.jpg"),
    Path("assets/backgrounds/sunny_meadows/sky.jpg"),
    Path("assets/map/map.jpg"),
}
UNSUPPORTED_WEB_SUFFIXES = {".mp3", ".webp"}


def main() -> None:
    """Fail when committed game assets exceed the web distribution budget."""
    files = [path for path in ASSET_DIRECTORY.rglob("*") if path.is_file()]
    unsupported = [
        path for path in files if path.suffix.lower() in UNSUPPORTED_WEB_SUFFIXES
    ]
    unexpected_jpegs = [
        path
        for path in files
        if path.suffix.lower() in {".jpg", ".jpeg"} and path not in ALLOWED_JPEG_FILES
    ]
    oversized = [path for path in files if path.stat().st_size > MAX_FILE_BYTES]
    total_bytes = sum(path.stat().st_size for path in files)
    if unsupported:
        paths = ", ".join(str(path) for path in unsupported)
        raise SystemExit(f"Assets use unsupported web formats: {paths}")
    if unexpected_jpegs:
        paths = ", ".join(str(path) for path in unexpected_jpegs)
        raise SystemExit(
            "JPEG is allowed only for reviewed opaque backgrounds: " f"{paths}"
        )
    if oversized:
        paths = ", ".join(str(path) for path in oversized)
        raise SystemExit(f"Assets exceed the 10 MiB per-file budget: {paths}")
    if total_bytes > MAX_TOTAL_BYTES:
        total_mib = total_bytes / (1024 * 1024)
        raise SystemExit(f"Assets exceed the 35 MiB budget: {total_mib:.1f} MiB")
    print(
        f"Asset budget passed: {len(files)} files, {total_bytes / (1024 * 1024):.1f} MiB"
    )


if __name__ == "__main__":
    main()
