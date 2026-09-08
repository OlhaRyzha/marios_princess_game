import random
from collections.abc import Callable
from typing import cast

import pygame

from game.core.background import ParallaxBackground
from game.core.boss_actor import BossActor
from game.core.boss_arena import BossArena
from game.core.camera import LevelCamera
from game.core.collectible_system import CollectibleSystem
from game.core.collision import CollisionSprite, collide_mask
from game.core.combat import CombatSystem
from game.core.demo_renderer import DemoRenderer
from game.core.effects import ConfettiBurst, HitSpark
from game.core.finale import FinaleCinematic
from game.core.obstacle_factory import boss_gate_position, build_obstacles
from game.core.player import Princess
from game.data.bosses import BOSS_ROSTER, BossConfig
from game.data.locations import NEXT_LOCATION, LocationName
from game.i18n import Localizer
from game.services.audio import AudioService
from game.state import SceneMode
from game.systems.input_state import InputSource
from game.systems.time_source import TimeSource
from game.ui.boss_preview import BossPreview
from game.ui.hud import HealthHUD
from game.ui.ui_modal import VictoryModal
from game.utils.constants import (
    DAMAGE_PER_HIT,
    FONT_SIZE,
    GROUND_Y,
    LEVEL_WIDTH,
    MUSIC_BOSS,
    MUSIC_LEVEL,
    MUSIC_VICTORY,
    OBSTACLE_SCALE,
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

        self.START_X = 240
        self.player: Princess = Princess(
            (self.START_X, GROUND_Y), time_source=self.time_source
        )

        self.all_sprites: pygame.sprite.Group = pygame.sprite.Group()
        self.obstacles: pygame.sprite.Group = pygame.sprite.Group()
        self.boss_group: pygame.sprite.Group = pygame.sprite.Group()
        self.fx_group: pygame.sprite.Group = pygame.sprite.Group()
        self.projectiles: pygame.sprite.Group = pygame.sprite.Group()
        self.collectible_system = CollectibleSystem(
            rng=self.rng,
            localizer=self.localizer,
        )
        self.collectibles = self.collectible_system.sprites
        self.all_sprites.add(self.player)

        self.combat = CombatSystem(
            self.player,
            self.boss_group,
            self.projectiles,
            self.fx_group,
            time_source=self.time_source,
            on_boss_defeated=self._on_boss_victory,
        )

        self.location: LocationName = location
        self.boss_gate_x = 0
        self._boss_trigger_rect = pygame.Rect(0, 0, 48, self.screen.get_height())

        self.camera = LevelCamera(WIDTH, LEVEL_WIDTH)
        self.boss_arena = BossArena(WIDTH, LEVEL_WIDTH)
        self.font = load_font(FONT_SIZE)
        self.hud = HealthHUD()
        self.renderer = DemoRenderer(
            screen=self.screen,
            font=self.font,
            hud=self.hud,
            localizer=self.localizer,
        )

        self.mode = SceneMode.EXPLORE
        self.current_boss: BossConfig | None = None
        self._completion_reported = False
        self._on_location_completed = on_location_completed
        self._on_game_finished = on_game_finished
        self.boss_preview = BossPreview(
            self.font,
            localizer=self.localizer,
            on_select=self._on_boss_selected,
        )
        self._boss_intro_shown = False

        self.victory_modal: VictoryModal | None = None
        self.finale = FinaleCinematic(duration_ms=3200, font_size=FONT_SIZE)
        self._collectible_hint_timer: float = 0.0
        self._collectible_hint_text: str = ""

        self._load_obstacles(location)

        self.audio_service.stop_music()
        self.audio_service.play_music(MUSIC_LEVEL, loop=True)

    def _load_obstacles(self, location: LocationName):

        old_obstacles = tuple(self.obstacles.sprites())
        if old_obstacles:
            self.all_sprites.remove(*old_obstacles)
        self.obstacles.empty()

        new_obstacles, max_right = build_obstacles(
            location=location,
            start_x=self.START_X,
            scale=OBSTACLE_SCALE,
            rng=self.rng,
        )
        if new_obstacles:
            self.obstacles.add(*new_obstacles)
            self.all_sprites.add(*new_obstacles)

        self.collectible_system.load(location)
        self.boss_gate_x = boss_gate_position(max_right)
        self._boss_trigger_rect = pygame.Rect(
            self.boss_gate_x, 0, 48, self.screen.get_height()
        )

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

    def _sync_player_rect(self) -> None:
        self.player.rect.midbottom = (int(self.player.pos.x), int(self.player.pos.y))

    def _on_boss_selected(self, boss: BossConfig) -> None:
        self.current_boss = boss
        self._start_boss_fight(boss)

    def _on_boss_victory(self) -> None:
        if not self._completion_reported and self._on_location_completed:
            self._completion_reported = True
            self._on_location_completed(self.location)

        self.boss_group.empty()
        self.projectiles.empty()
        self.audio_service.stop_music()
        self.audio_service.play_music(MUSIC_VICTORY, loop=False)
        self.fx_group.add(
            ConfettiBurst(
                self.screen.get_rect(),
                time_source=self.time_source,
                rng=self.rng,
            )
        )

        nxt = NEXT_LOCATION.get(self.location)
        if nxt:
            title = self.localizer.text("victory.title")
            lines = [
                self.localizer.text("victory.boss"),
                "",
                self.localizer.text("victory.next_goal"),
                self.localizer.text(
                    "victory.next", location=nxt.replace("_", " ").title()
                ),
            ]
            modal = VictoryModal(
                title=title,
                lines=lines,
                on_continue=lambda: self.switch_location(nxt),
                localizer=self.localizer,
            )
            self.victory_modal = modal
            self.mode = SceneMode.VICTORY
        else:
            self.finale.ensure_assets()
            self.finale.start(self.time_source.now_ms())
            self.mode = SceneMode.FINALE

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

    def _handle_obstacle_collisions(self):
        if self.mode is not SceneMode.EXPLORE:
            return
        hits = [
            obstacle
            for obstacle in self.obstacles
            if collide_mask(
                cast(CollisionSprite, self.player), cast(CollisionSprite, obstacle)
            )
        ]
        if hits and self.player.can_take_damage():
            self.player.take_damage(DAMAGE_PER_HIT)
            self.player.pos.x += -18 if self.player.dir > 0 else 18
            self.player.rect.x = int(self.player.pos.x)

    def _collect_collectibles(self):
        if self.mode is not SceneMode.EXPLORE:
            return
        for position in self.collectible_system.collect(self.player.rect):
            self.fx_group.add(HitSpark(position, time_source=self.time_source))

    def _check_boss_gate(self):
        if self._boss_intro_shown or self.mode is not SceneMode.EXPLORE:
            return
        if self.player.rect.right >= self._boss_trigger_rect.left:
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
        self._load_obstacles(location)

        self.player.pos.update(self.START_X, GROUND_Y)
        self._sync_player_rect()

        self.camera.reset()
        self.mode = SceneMode.EXPLORE
        self._boss_intro_shown = False
        self._completion_reported = False
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
            self._handle_obstacle_collisions()
            self._collect_collectibles()
            self._check_boss_gate()
        elif self.mode is SceneMode.BOSS:
            self.combat.update_boss_phase()
        elif self.mode is SceneMode.FINALE:
            now = self.time_source.now_ms()
            if self.finale.ready_for_modal(now):
                self.finale.reset()
                if self._on_game_finished:
                    self._on_game_finished()

        if self.player.health <= 0:
            self.player.health = self.player.max_health
            self.switch_location(self.location)

    def draw(self) -> None:
        self.renderer.draw(self)
