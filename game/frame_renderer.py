from typing import Protocol

import pygame

from game.state import GameMode, GameState
from game.ui.start_menu import StartMenu
from game.ui.world_map import WorldMapScene
from game.utils.constants import HEIGHT, WIDTH
from game.utils.fonts import load_font


class DrawableScene(Protocol):
    def draw(self) -> None: ...


class FrameRenderer[SceneT: DrawableScene]:
    def __init__(
        self,
        *,
        screen: pygame.Surface,
        menu: StartMenu,
        world_map: WorldMapScene,
    ) -> None:
        self.screen = screen
        self.menu = menu
        self.world_map = world_map
        self.loading_font = load_font(42)

    def draw_loading(self) -> None:
        """Show immediate feedback before expensive scene construction."""
        self.menu.draw(self.screen)
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((30, 20, 40, 165))
        self.screen.blit(overlay, (0, 0))
        text = self.loading_font.render(
            self.menu.localizer.text("game.loading"), True, (255, 245, 250)
        )
        self.screen.blit(text, text.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
        pygame.display.flip()

    def draw(self, state: GameState[SceneT]) -> None:
        if state.mode is GameMode.MENU:
            self.menu.draw(self.screen)
        elif state.mode is GameMode.MAP:
            self.world_map.draw(self.screen, overlay=False)
        elif state.mode is GameMode.GAME and state.scene is not None:
            state.scene.draw()
        elif state.mode is GameMode.MAP_OVERLAY:
            if state.scene is not None:
                state.scene.draw()
            self.world_map.draw(self.screen, overlay=True)
        elif state.mode is GameMode.MENU_PAUSE:
            if state.scene is not None:
                state.scene.draw()
            dim = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            dim.fill((0, 0, 0, 110))
            self.screen.blit(dim, (0, 0))
            self.menu.draw(self.screen)

        pygame.display.flip()
