from collections.abc import Iterable
from dataclasses import dataclass, field

from game.data.locations import LOCATION_ORDER, LocationName


@dataclass(slots=True)
class WorldMapState:
    """Own map selection and level progression independently of rendering."""

    locations: list[LocationName]
    unlocked: set[LocationName] = field(default_factory=set)
    completed: set[LocationName] = field(default_factory=set)
    selected_index: int = 0

    def __post_init__(self) -> None:
        self._unlock_first_location()
        self.focus_unlocked_location()

    @property
    def selected_location(self) -> LocationName:
        return self.locations[self.selected_index]

    @property
    def mario_location(self) -> LocationName | None:
        if not self.locations:
            return None
        ordered: list[LocationName] = [
            location for location in LOCATION_ORDER if location in self.locations
        ]
        if not ordered:
            ordered = list(self.locations)
        for location in reversed(ordered):
            if location in self.completed:
                return location
        for location in ordered:
            if location in self.unlocked:
                return location
        return ordered[0]

    def move(self, offset: int) -> None:
        if self.locations:
            self.selected_index = (self.selected_index + offset) % len(self.locations)

    def select(self, location: LocationName) -> None:
        self.selected_index = self.locations.index(location)

    def is_unlocked(self, location: LocationName) -> bool:
        return location in self.unlocked

    def set_progress(
        self, *, unlocked: Iterable[LocationName], completed: Iterable[LocationName]
    ) -> None:
        self.unlocked = set(unlocked)
        self.completed = set(completed)
        self._unlock_first_location()
        self.focus_unlocked_location()

    def focus_unlocked_location(self) -> None:
        if not self.locations:
            self.selected_index = 0
            return
        self.selected_index = max(0, min(self.selected_index, len(self.locations) - 1))
        if self.selected_location in self.unlocked:
            return
        for index, location in enumerate(self.locations):
            if location in self.unlocked:
                self.selected_index = index
                return

    def _unlock_first_location(self) -> None:
        if not self.unlocked and self.locations:
            self.unlocked.add(self.locations[0])
