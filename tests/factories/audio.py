from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class RecordingAudioService:
    played_tracks: list[tuple[str | Path, bool]] = field(default_factory=list)
    stop_count: int = 0
    arm_count: int = 0
    armed: bool = False

    def arm(self) -> bool:
        self.arm_count += 1
        self.armed = True
        return True

    def play_music(self, path: str | Path, *, loop: bool = True) -> None:
        self.played_tracks.append((path, loop))

    def stop_music(self) -> None:
        self.stop_count += 1
