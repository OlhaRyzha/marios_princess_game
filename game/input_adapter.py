from typing import Protocol

import pygame

from game.controller import ControllerEffect, GameController
from game.services.audio import AudioService
from game.state import GameMode
from game.systems.input_state import InputSource
from game.ui.start_menu import StartMenu
from game.ui.world_map import WorldMapScene


class EventScene(Protocol):
    def handle_event(self, event: pygame.event.Event) -> None: ...


class InputAdapter[SceneT: EventScene]:
    def __init__(
        self,
        *,
        controller: GameController[SceneT],
        menu: StartMenu,
        world_map: WorldMapScene,
        audio_service: AudioService,
        input_source: InputSource,
        is_web: bool,
    ) -> None:
        self.controller = controller
        self.menu = menu
        self.world_map = world_map
        self.audio_service = audio_service
        self.input_source = input_source
        self.is_web = is_web

    def route(self, event: pygame.event.Event) -> ControllerEffect | None:
        state = self.controller.state
        if state.mode is GameMode.GAME:
            self.input_source.handle_event(event)

        if event.type == pygame.QUIT:
            self.controller.stop()
            return None

        if self.is_web and event.type in (
            pygame.KEYDOWN,
            pygame.MOUSEBUTTONDOWN,
        ):
            if not state.audio_armed:
                state.audio_armed = self.audio_service.arm()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m and self.controller.toggle_map():
                return None
            if (
                event.key == pygame.K_ESCAPE
                and not self.menu.controls_open
                and self.controller.handle_escape()
            ):
                return None

        if state.mode in (GameMode.MENU, GameMode.MENU_PAUSE):
            return self.controller.handle_menu(self.menu.handle_event(event))
        if state.mode in (GameMode.MAP, GameMode.MAP_OVERLAY):
            return self.controller.handle_map(self.world_map.handle_event(event))
        if state.mode is GameMode.GAME and state.scene is not None:
            state.scene.handle_event(event)
        return None
