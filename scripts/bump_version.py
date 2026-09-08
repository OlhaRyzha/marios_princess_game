import argparse
import re
from pathlib import Path

PROJECT_FILE = Path(__file__).resolve().parents[1] / "pyproject.toml"
VERSION_LINE = re.compile(r'(?m)^version = "(\d+)\.(\d+)\.(\d+)"$')


def bump_version(content: str, part: str) -> tuple[str, str]:
    """Increment one SemVer component in pyproject content."""
    match = VERSION_LINE.search(content)
    if match is None:
        raise ValueError("pyproject.toml does not contain a SemVer project version")
    major, minor, patch = (int(value) for value in match.groups())
    if part == "major":
        major, minor, patch = major + 1, 0, 0
    elif part == "minor":
        minor, patch = minor + 1, 0
    elif part == "patch":
        patch += 1
    else:
        raise ValueError(f"Unsupported version part: {part}")
    version = f"{major}.{minor}.{patch}"
    updated = VERSION_LINE.sub(f'version = "{version}"', content, count=1)
    return updated, version


def main() -> None:
    """Update the project version and print it for release automation."""
    parser = argparse.ArgumentParser(description="Increment the project version")
    parser.add_argument("part", choices=("patch", "minor", "major"))
    arguments = parser.parse_args()
    updated, version = bump_version(PROJECT_FILE.read_text(), arguments.part)
    PROJECT_FILE.write_text(updated)
    print(version)


if __name__ == "__main__":
    main()
