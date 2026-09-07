import json
import platform
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, cast

from game.data.locations import LOCATION_ORDER, LocationName

STORAGE_KEY = "marios-princess-progress"


@dataclass(frozen=True, slots=True)
class ProgressSnapshot:
    unlocked: frozenset[LocationName]
    completed: frozenset[LocationName]
    pending_location: LocationName


class ProgressStore(Protocol):
    def load(self) -> ProgressSnapshot | None: ...

    def save(self, snapshot: ProgressSnapshot) -> None: ...


def _to_json(snapshot: ProgressSnapshot) -> str:
    payload = {
        "unlocked": sorted(snapshot.unlocked),
        "completed": sorted(snapshot.completed),
        "pending_location": snapshot.pending_location,
    }
    return json.dumps(payload, separators=(",", ":"))


def _locations(values: Iterable[object]) -> frozenset[LocationName]:
    valid_locations = set(LOCATION_ORDER)
    return frozenset(
        value for value in values if isinstance(value, str) and value in valid_locations
    )


def _from_json(content: str) -> ProgressSnapshot | None:
    try:
        payload = json.loads(content)
    except (json.JSONDecodeError, TypeError):
        return None
    if not isinstance(payload, dict):
        return None

    unlocked_value = payload.get("unlocked", [])
    completed_value = payload.get("completed", [])
    pending_value = payload.get("pending_location", LOCATION_ORDER[0])
    if not isinstance(unlocked_value, list) or not isinstance(completed_value, list):
        return None
    if not isinstance(pending_value, str) or pending_value not in LOCATION_ORDER:
        pending_value = LOCATION_ORDER[0]

    unlocked = _locations(unlocked_value) or frozenset({LOCATION_ORDER[0]})
    return ProgressSnapshot(
        unlocked=unlocked,
        completed=_locations(completed_value),
        pending_location=pending_value,
    )


class JsonProgressStore:
    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> ProgressSnapshot | None:
        try:
            return _from_json(self.path.read_text(encoding="utf-8"))
        except OSError:
            return None

    def save(self, snapshot: ProgressSnapshot) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self.path.with_suffix(".tmp")
        temporary_path.write_text(_to_json(snapshot), encoding="utf-8")
        temporary_path.replace(self.path)


class BrowserStorage(Protocol):
    def getItem(self, key: str) -> str | None: ...

    def setItem(self, key: str, value: str) -> None: ...


class BrowserWindow(Protocol):
    localStorage: BrowserStorage


class BrowserProgressStore:
    def __init__(self, storage: BrowserStorage) -> None:
        self.storage = storage

    def load(self) -> ProgressSnapshot | None:
        content = self.storage.getItem(STORAGE_KEY)
        return _from_json(content) if content else None

    def save(self, snapshot: ProgressSnapshot) -> None:
        self.storage.setItem(STORAGE_KEY, _to_json(snapshot))


def create_progress_store(*, is_web: bool) -> ProgressStore:
    if is_web:
        window_object: object = vars(platform)["window"]
        window = cast(BrowserWindow, window_object)
        return BrowserProgressStore(window.localStorage)
    return JsonProgressStore(Path.home() / ".marios_princess_game" / "progress.json")
