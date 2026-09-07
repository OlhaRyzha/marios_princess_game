from pathlib import Path

from game.utils.constants import BASE_DIR


def resolve_project_path(path: str | Path) -> Path:
    candidate = Path(path).expanduser()
    if candidate.is_absolute():
        return candidate
    return BASE_DIR / candidate
