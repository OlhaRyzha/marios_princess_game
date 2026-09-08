from enum import Enum, auto

from game.actions import MapAction, MapEvent, MenuAction
from game.data.locations import LocationName
from game.state import GameMode, GameState


class ControllerEffect(Enum):
    START_SCENE = auto()
    OPEN_CONTROLS = auto()


class GameController[SceneT]:
    def __init__(self, state: GameState[SceneT]) -> None:
        self.state = state

    def stop(self) -> None:
        self.state.running = False

    def return_to_menu(self) -> None:
        """Leave the active game session and restore the main menu."""
        self.state.mode = GameMode.MENU
        self.state.scene = None
        self.state.scene_load_pending = False
        self.state.time_accumulator = 0.0

    def handle_escape(self) -> bool:
        transitions = {
            GameMode.GAME: GameMode.MENU_PAUSE,
            GameMode.MENU_PAUSE: GameMode.GAME,
            GameMode.MAP: GameMode.MENU,
            GameMode.MAP_OVERLAY: GameMode.GAME,
        }
        next_mode = transitions.get(self.state.mode)
        if next_mode is None:
            return False
        self.state.mode = next_mode
        return True

    def toggle_map(self) -> bool:
        if self.state.scene is None:
            return False
        if self.state.mode is GameMode.GAME:
            self.state.mode = GameMode.MAP_OVERLAY
            return True
        if self.state.mode is GameMode.MAP_OVERLAY:
            self.state.mode = GameMode.GAME
            return True
        return False

    def handle_menu(self, action: MenuAction | None) -> ControllerEffect | None:
        if action is None:
            return None
        if action is MenuAction.START_GAME:
            self.state.mode = GameMode.GAME
            return ControllerEffect.START_SCENE
        if action is MenuAction.RESUME_GAME:
            self.state.mode = GameMode.GAME
            return None
        if action is MenuAction.OPEN_MAP:
            self.state.mode = (
                GameMode.MAP_OVERLAY
                if self.state.mode is GameMode.MENU_PAUSE
                else GameMode.MAP
            )
            return None
        if action is MenuAction.OPEN_CONTROLS:
            return ControllerEffect.OPEN_CONTROLS
        if action is MenuAction.RETURN_TO_MENU:
            self.return_to_menu()
            return None
        if action is MenuAction.QUIT:
            self.stop()
        return None

    def handle_map(self, event: MapEvent | None) -> ControllerEffect | None:
        if event is None:
            return None
        if event.action is MapAction.BACK:
            self.state.mode = (
                GameMode.GAME
                if self.state.mode is GameMode.MAP_OVERLAY
                else GameMode.MENU
            )
            return None
        if (
            event.action is MapAction.START
            and event.location is not None
            and self.state.progress.select(event.location)
        ):
            self.state.mode = GameMode.GAME
            return ControllerEffect.START_SCENE
        return None

    def complete_location(self, location: LocationName) -> bool:
        return self.state.progress.complete(location)
