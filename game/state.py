from dataclasses import dataclass, field
from enum import StrEnum

from game.data.locations import LOCATION_ORDER, NEXT_LOCATION, LocationName


class GameMode(StrEnum):
    MENU = "menu"
    MAP = "map"
    GAME = "game"
    MAP_OVERLAY = "map_overlay"
    MENU_PAUSE = "menu_pause"


class SceneMode(StrEnum):
    EXPLORE = "explore"
    BOSS = "boss"
    FINALE = "finale"
    VICTORY = "victory"


@dataclass(slots=True)
class Progress:
    unlocked: set[LocationName] = field(default_factory=lambda: {LOCATION_ORDER[0]})
    completed: set[LocationName] = field(default_factory=set[LocationName])
    pending_location: LocationName = LOCATION_ORDER[0]

    def complete(self, location: LocationName) -> bool:
        """Complete a location and unlock the next one exactly once."""
        if location in self.completed:
            return False

        self.completed.add(location)
        next_location = NEXT_LOCATION[location]
        if next_location is not None:
            self.unlocked.add(next_location)
            self.pending_location = next_location
        return True

    def select(self, location: LocationName) -> bool:
        """Select an unlocked location as the next scene."""
        if location not in self.unlocked:
            return False
        self.pending_location = location
        return True


@dataclass(slots=True)
class GameState[SceneT]:
    mode: GameMode = GameMode.MENU
    progress: Progress = field(default_factory=Progress)
    scene: SceneT | None = None
    running: bool = True
    audio_armed: bool = False
    time_accumulator: float = 0.0
    scene_load_pending: bool = False
