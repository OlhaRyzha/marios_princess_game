import json
import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")


def read_versions() -> tuple[str, str]:
    """Read the project and release manifest versions."""
    with (ROOT / "pyproject.toml").open("rb") as file:
        project_version = tomllib.load(file)["project"]["version"]
    manifest = json.loads((ROOT / ".release-please-manifest.json").read_text())
    return project_version, manifest["."]


def main() -> None:
    """Ensure release metadata contains one synchronized SemVer version."""
    project_version, manifest_version = read_versions()
    if project_version != manifest_version:
        raise SystemExit(
            f"Version mismatch: pyproject={project_version}, manifest={manifest_version}"
        )
    if SEMVER.fullmatch(project_version) is None:
        raise SystemExit(f"Version is not valid SemVer: {project_version}")
    print(f"Version metadata passed: {project_version}")


if __name__ == "__main__":
    main()
