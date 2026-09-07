from pathlib import Path

from game.app import GameRuntime
from game.services.progress import JsonProgressStore, ProgressSnapshot
from tests.factories.progress import MemoryProgressStore


def test_json_progress_store_round_trip(tmp_path: Path) -> None:
    store = JsonProgressStore(tmp_path / "progress.json")
    snapshot = ProgressSnapshot(
        unlocked=frozenset({"sunny_meadows", "mushroom_woods"}),
        completed=frozenset({"sunny_meadows"}),
        pending_location="mushroom_woods",
    )

    store.save(snapshot)

    assert store.load() == snapshot


def test_runtime_restores_saved_progress(pygame_runtime: None) -> None:
    snapshot = ProgressSnapshot(
        unlocked=frozenset({"sunny_meadows", "mushroom_woods"}),
        completed=frozenset({"sunny_meadows"}),
        pending_location="mushroom_woods",
    )
    runtime = GameRuntime(
        is_web=False,
        progress_store=MemoryProgressStore(snapshot),
    )

    assert runtime.state.progress.unlocked == set(snapshot.unlocked)
    assert runtime.state.progress.completed == set(snapshot.completed)
    assert runtime.state.progress.pending_location == "mushroom_woods"


def test_invalid_progress_file_is_ignored(tmp_path: Path) -> None:
    path = tmp_path / "progress.json"
    path.write_text("not-json", encoding="utf-8")

    assert JsonProgressStore(path).load() is None
