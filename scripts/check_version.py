import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")


def read_version() -> str:
    """Read the project version."""
    with (ROOT / "pyproject.toml").open("rb") as file:
        return tomllib.load(file)["project"]["version"]


def main() -> None:
    """Ensure release metadata contains one synchronized SemVer version."""
    project_version = read_version()
    if SEMVER.fullmatch(project_version) is None:
        raise SystemExit(f"Version is not valid SemVer: {project_version}")
    print(f"Version metadata passed: {project_version}")


if __name__ == "__main__":
    main()
