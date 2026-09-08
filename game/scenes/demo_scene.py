import random
from collections.abc import Callable
from typing import cast

import pygame

from game.combat.boss_actor import BossActor
from game.combat.boss_arena import BossArena
from game.combat.combat import CombatSystem
from game.data.bosses import BOSS_ROSTER, BossConfig
from game.data.locations import LocationName
from game.i18n import Localizer
from game.levels.demo_level import DemoLevel
from game.presentation.background import ParallaxBackground
from game.presentation.camera import LevelCamera
from game.scenes.demo_progression import DemoProgression
from game.scenes.demo_renderer import DemoRenderer
from game.services.audio import AudioService
from game.state import SceneMode
from game.systems.input_state import InputSource
from game.systems.time_source import TimeSource
from game.ui.boss_preview import BossPreview
from game.ui.hud import HealthHUD
from game.ui.ui_modal import VictoryModal
from game.utils.constants import (
    FONT_SIZE,
    LEVEL_WIDTH,
    MUSIC_BOSS,
    MUSIC_LEVEL,
    WIDTH,
)
from game.utils.fonts import load_font


class DemoScene:
    def __init__(
        self,
        screen: "pygame.Surface",
        location: LocationName = "sunny_meadows",
        *,
        time_source: TimeSource,
        input_source: InputSource,
        rng: random.Random,
        audio_service: AudioService,
        localizer: Localizer | None = None,
        on_location_completed: Callable[[LocationName], None] | None = None,
        on_game_finished: Callable[[], None] | None = None,
    ):
        self.screen = screen
        self.time_source = time_source
        self.input_source = input_source
        self.rng = rng
        self.audio_service = audio_service
        self.localizer = localizer or Localizer()
        self.bg = ParallaxBackground(location)
        self.level = DemoLevel(
            screen_height=self.screen.get_height(),
            location=location,
            time_source=self.time_source,
            rng=self.rng,
            localizer=self.localizer,
        )
        self._bind_level_components()
        self._create_gameplay_services(location)
        self._create_ui()
        self._create_progression(on_location_completed, on_game_finished)
        self._reset_transient_state()
        self.audio_service.stop_music()
        self.audio_service.play_music(MUSIC_LEVEL, loop=True)

    def _bind_level_components(self) -> None:
        """Expose the active level components used by scene collaborators."""
        self.player = self.level.player
        self.all_sprites = self.level.all_sprites
        self.obstacles = self.level.obstacles
        self.boss_group = self.level.boss_group
        self.fx_group = self.level.fx_group
        self.projectiles = self.level.projectiles
        self.collectible_system = self.level.collectible_system
        self.collectibles = self.collectible_system.sprites

    def _create_gameplay_services(self, location: LocationName) -> None:
        """Create combat and camera services for the active level."""
        self.combat = CombatSystem(
            self.player,
            self.boss_group,
            self.projectiles,
            self.fx_group,
            time_source=self.time_source,
            on_boss_defeated=self._on_boss_victory,
        )
        self.location: LocationName = location
        self.boss_gate_x = self.level.boss_gate_x
        self.camera = LevelCamera(WIDTH, LEVEL_WIDTH)
        self.boss_arena = BossArena(WIDTH, LEVEL_WIDTH)

    def _create_ui(self) -> None:
        """Create scene presentation components."""
        self.font = load_font(FONT_SIZE)
        self.hud = HealthHUD()
        self.renderer = DemoRenderer(
            screen=self.screen,
            font=self.font,
            hud=self.hud,
            localizer=self.localizer,
        )

    def _create_progression(
        self,
        on_location_completed: Callable[[LocationName], None] | None,
        on_game_finished: Callable[[], None] | None,
    ) -> None:
        """Create progression callbacks and the boss selection UI."""
        self.mode = SceneMode.EXPLORE
        self.current_boss: BossConfig | None = None
        self.progression = DemoProgression(
            screen=self.screen,
            time_source=self.time_source,
            audio_service=self.audio_service,
            localizer=self.localizer,
            rng=self.rng,
            on_location_completed=on_location_completed,
            on_game_finished=on_game_finished,
        )
        self.boss_preview = BossPreview(
            self.font,
            localizer=self.localizer,
            on_select=self._on_boss_selected,
        )

    def _reset_transient_state(self) -> None:
        """Reset overlays and short-lived scene feedback."""
        self._boss_intro_shown = False
        self.victory_modal: VictoryModal | None = None
        self.finale = self.progression.finale
        self._collectible_hint_timer: float = 0.0
        self._collectible_hint_text: str = ""

    def handle_event(self, event: "pygame.event.Event") -> None:
        if self.victory_modal and self.victory_modal.active:
            self.victory_modal.handle_event(event)
            return
        if self.boss_preview and self.boss_preview.active:
            self.boss_preview.handle_key(event)

    def _update_camera(self):
        if self.mode is not SceneMode.BOSS:
            self.camera.follow(self.player.pos.x)

    def _keep_boss_fight_visible(self) -> None:
        if self.mode is not SceneMode.BOSS:
            return
        boss = next(iter(self.boss_group), None)
        if boss is None:
            return
        self.boss_arena.keep_actors_visible(
            player=self.player,
            boss=cast(BossActor, boss),
            camera_x=self.camera_x,
        )

    @property
    def camera_x(self) -> float:
        return self.camera.x

    @camera_x.setter
    def camera_x(self, value: float) -> None:
        self.camera.x = value

    def _on_boss_selected(self, boss: BossConfig) -> None:
        self.current_boss = boss
        self._start_boss_fight(boss)

    def _on_boss_victory(self) -> None:
        self.boss_group.empty()
        self.projectiles.empty()
        self.mode, self.victory_modal = self.progression.complete_boss(
            location=self.location,
            effects=self.fx_group,
            on_continue=self.switch_location,
        )

    def _start_boss_fight(self, boss: BossConfig) -> None:
        self.mode = SceneMode.BOSS
        self.audio_service.stop_music()
        self.audio_service.play_music(MUSIC_BOSS, loop=True)

        boss_actor, self.camera_x = self.boss_arena.arrange(
            player=self.player,
            boss=boss,
            camera_x=self.camera_x,
            time_source=self.time_source,
        )
        self.combat.start_boss(boss_actor)

    def _check_boss_gate(self):
        if self._boss_intro_shown or self.mode is not SceneMode.EXPLORE:
            return
        if self.level.reached_boss_gate():
            if not self.collectible_system.complete:
                self._collectible_hint_text = (
                    f"{self.collectible_system.hint} "
                    f"({self.collectible_system.collected}/{self.collectible_system.goal})"
                )
                self._collectible_hint_timer = 2.6
                return
            bosses = BOSS_ROSTER[self.location]
            if bosses:
                self.boss_preview.open(bosses)
            self._boss_intro_shown = True

    def switch_location(self, location: LocationName):
        self.bg.set_location(location)
        self.location = location
        self.level.load(location)
        self.boss_gate_x = self.level.boss_gate_x
        self.level.reset_player()

        self.camera.reset()
        self.mode = SceneMode.EXPLORE
        self._boss_intro_shown = False
        self.progression.reset()
        self.current_boss = None
        self.boss_group.empty()
        self.fx_group.empty()
        self.projectiles.empty()
        self.victory_modal = None
        self._collectible_hint_timer = 0.0
        self._collectible_hint_text = ""
        self.finale.reset()
        self.audio_service.stop_music()
        self.audio_service.play_music(MUSIC_LEVEL, loop=True)

    def update(self, dt: float):
        input_state = self.input_source.read()
        self.all_sprites.update(dt, input_state)
        self.collectibles.update(dt)

        self.combat.update(dt)
        self._keep_boss_fight_visible()
        self._update_camera()
        if self._collectible_hint_timer > 0.0:
            self._collectible_hint_timer = max(0.0, self._collectible_hint_timer - dt)

        if self.mode is SceneMode.EXPLORE:
            self.level.update_exploration(self.mode, self.time_source)
            self._check_boss_gate()
        elif self.mode is SceneMode.BOSS:
            self.combat.update_boss_phase()
        elif self.mode is SceneMode.FINALE:
            self.progression.update_finale()

        if self.player.health <= 0:
            self.player.health = self.player.max_health
            self.switch_location(self.location)

    def draw(self) -> None:
        self.renderer.draw(self)
