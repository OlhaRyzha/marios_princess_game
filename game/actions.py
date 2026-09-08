from dataclasses import dataclass
from enum import StrEnum

from game.data.locations import LocationName


class MenuAction(StrEnum):
    START_GAME = "start_game"
    OPEN_MAP = "open_map"
    OPEN_CONTROLS = "open_controls"
    RESUME_GAME = "resume_game"
    RETURN_TO_MENU = "return_to_menu"
    QUIT = "quit"


@dataclass(frozen=True, slots=True)
class MenuItem:
    label_key: str
    action: MenuAction


class MapAction(StrEnum):
    START = "start"
    BACK = "back"


@dataclass(frozen=True, slots=True)
class MapEvent:
    action: MapAction
    location: LocationName | None = None
