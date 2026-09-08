from pathlib import Path

ASSET_DIRECTORY = Path("assets")
MAX_FILE_BYTES = 10 * 1024 * 1024
MAX_TOTAL_BYTES = 35 * 1024 * 1024


def main() -> None:
    """Fail when committed game assets exceed the web distribution budget."""
    files = [path for path in ASSET_DIRECTORY.rglob("*") if path.is_file()]
    oversized = [path for path in files if path.stat().st_size > MAX_FILE_BYTES]
    total_bytes = sum(path.stat().st_size for path in files)
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
