from game.services.progress import ProgressSnapshot


class MemoryProgressStore:
    def __init__(self, snapshot: ProgressSnapshot | None = None) -> None:
        self.snapshot = snapshot
        self.save_count = 0

    def load(self) -> ProgressSnapshot | None:
        return self.snapshot

    def save(self, snapshot: ProgressSnapshot) -> None:
        self.snapshot = snapshot
        self.save_count += 1
