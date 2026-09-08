from typing import Protocol

import pygame

from game.gameplay.collectible_system import CollectibleSystem
from game.gameplay.player import Princess
from game.i18n import Localizer
from game.presentation.background import ParallaxBackground
from game.scenes.finale import FinaleCinematic
from game.state import SceneMode
from game.ui.boss_preview import BossPreview
from game.ui.hud import HealthHUD
from game.ui.ui_modal import VictoryModal
from game.utils.constants import BOSS_DIM_COLOR, GROUND_Y, WIDTH


class DemoView(Protocol):
    screen: pygame.Surface
    bg: ParallaxBackground
    mode: SceneMode
    boss_gate_x: int
    obstacles: pygame.sprite.Group
    collectibles: pygame.sprite.Group
    projectiles: pygame.sprite.Group
    boss_group: pygame.sprite.Group
    fx_group: pygame.sprite.Group
    player: Princess
    collectible_system: CollectibleSystem
    victory_modal: VictoryModal | None
    boss_preview: BossPreview
    _collectible_hint_timer: float
    _collectible_hint_text: str
    finale: FinaleCinematic

    @property
    def camera_x(self) -> float: ...


class DemoRenderer:
    """Render a gameplay scene without changing its state."""

    def __init__(
        self,
        *,
        screen: pygame.Surface,
        font: pygame.font.Font,
        hud: HealthHUD,
        localizer: Localizer,
    ) -> None:
        self.screen = screen
        self.font = font
        self.hud = hud
        self.localizer = localizer

    def _draw_boss_health(self, scene: DemoView) -> None:
        boss = next(iter(scene.boss_group), None)
        if boss is None:
            return
        width, height = 320, 16
        x = (self.screen.get_width() - width) // 2 + 72
        y = 64
        pygame.draw.rect(
            self.screen, (30, 30, 30), (x, y, width, height), border_radius=6
        )
        pygame.draw.rect(
            self.screen,
            (220, 220, 220),
            (x, y, width, height),
            2,
            border_radius=6,
        )
        ratio = boss.health / boss.max_health if boss.max_health > 0 else 0
        pygame.draw.rect(
            self.screen,
            (220, 70, 70),
            (x + 2, y + 2, int((width - 4) * ratio), height - 4),
            border_radius=5,
        )
        name = self.font.render(boss.name, True, (240, 240, 240))
        self.screen.blit(name, (x + (width - name.get_width()) // 2, y + height + 6))

    def _draw_exploration(self, scene: DemoView) -> None:
        for sprite in scene.obstacles:
            self.screen.blit(sprite.image, sprite.rect.move(-scene.camera_x, 0))
        flag_x = int(scene.boss_gate_x - scene.camera_x)
        if 0 <= flag_x <= WIDTH:
            pole = pygame.Rect(flag_x, int(GROUND_Y - 120), 4, 120)
            pygame.draw.rect(self.screen, (60, 60, 60), pole)
            pygame.draw.polygon(
                self.screen,
                (240, 72, 72),
                [
                    (flag_x + 4, GROUND_Y - 120),
                    (flag_x + 40, GROUND_Y - 104),
                    (flag_x + 4, GROUND_Y - 88),
                ],
            )

    def _draw_actors(self, scene: DemoView) -> None:
        for projectile in scene.projectiles:
            self.screen.blit(projectile.image, projectile.rect.move(-scene.camera_x, 0))
        for boss in scene.boss_group:
            boss.draw(self.screen, scene.camera_x)
        for effect in scene.fx_group:
            effect.draw(self.screen, scene.camera_x)
        scene.player.draw(self.screen, scene.camera_x)

    def _draw_hud(self, scene: DemoView) -> None:
        progress = None
        icon = None
        if scene.collectible_system.goal:
            progress = scene.collectible_system.progress
            icon = scene.collectible_system.icon
        self.hud.draw(
            self.screen,
            scene.player.health,
            scene.player.max_health,
            collectibles=progress,
            icon=icon,
        )
        if scene.mode is SceneMode.BOSS:
            self._draw_boss_health(scene)
        tip = self.font.render(self.localizer.text("game.help"), True, (230, 230, 230))
        self.screen.blit(tip, (16, 12))
        if scene._collectible_hint_timer > 0 and scene._collectible_hint_text:
            hint = self.font.render(scene._collectible_hint_text, True, (255, 236, 210))
            self.screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, 70))

    def draw(self, scene: DemoView) -> None:
        """Draw the current gameplay frame and active overlay."""
        if scene.mode is SceneMode.FINALE:
            scene.finale.draw(self.screen)
        else:
            scene.bg.draw(self.screen, scene.camera_x)
            if scene.mode is SceneMode.EXPLORE:
                self._draw_exploration(scene)
            for item in scene.collectibles:
                self.screen.blit(item.image, item.rect.move(-scene.camera_x, 0))
            if scene.mode is SceneMode.BOSS:
                dim = pygame.Surface((WIDTH, self.screen.get_height()), pygame.SRCALPHA)
                dim.fill(BOSS_DIM_COLOR)
                self.screen.blit(dim, (0, 0))
            self._draw_actors(scene)
            self._draw_hud(scene)

        if scene.victory_modal and scene.victory_modal.active:
            scene.victory_modal.draw(self.screen)
        elif scene.boss_preview and not scene.boss_preview.is_done():
            scene.boss_preview.draw(self.screen)
