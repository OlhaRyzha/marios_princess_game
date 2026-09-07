import random
from collections.abc import Callable
from typing import cast

import pygame
from pygame.sprite import Group

from game.core.background import ParallaxBackground
from game.core.boss_arena import BossArena
from game.core.camera import LevelCamera
from game.core.collectible_system import CollectibleSystem
from game.core.collision import CollisionSprite, collide_mask
from game.core.combat import CombatSystem
from game.core.effects import ConfettiBurst, HitSpark
from game.core.finale import FinaleCinematic
from game.core.obstacle_factory import boss_gate_position, build_obstacles
from game.core.player import Princess
from game.data.bosses import BOSS_ROSTER, BossConfig
from game.data.locations import NEXT_LOCATION, LocationName
from game.i18n import Localizer
from game.services.audio import AudioService
from game.systems.input_state import InputSource
from game.systems.time_source import TimeSource
from game.ui.boss_preview import BossPreview
from game.ui.hud import HealthHUD
from game.ui.ui_modal import VictoryModal
from game.utils.constants import (
    BOSS_DIM_COLOR,
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
    @staticmethod
    def _post_quit_event() -> None:
        pygame.event.post(pygame.event.Event(pygame.QUIT))

    def __init__(
        self,
        screen: pygame.Surface,
        location: LocationName = "sunny_meadows",
        *,
        time_source: TimeSource,
        input_source: InputSource,
        rng: random.Random,
        audio_service: AudioService,
        localizer: Localizer | None = None,
        on_location_completed: Callable[[LocationName], None] | None = None,
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

        self.all_sprites: Group = Group()
        self.obstacles: Group = Group()
        self.boss_group: Group = Group()
        self.fx_group: Group = Group()
        self.projectiles: Group = Group()
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

        self.mode = "explore"
        self.current_boss: BossConfig | None = None
        self._completion_reported = False
        self._on_location_completed = on_location_completed
        self.boss_preview = BossPreview(
            self.font,
            localizer=self.localizer,
            on_select=self._on_boss_selected,
        )
        self._boss_intro_shown = False

        self.victory_modal: VictoryModal | None = None
        self.finale = FinaleCinematic(duration_ms=3200, font_size=FONT_SIZE)
        self._pending_final_modal: tuple[str, list[str]] | None = None
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

    def handle_event(self, event: pygame.event.Event) -> None:
        if self.victory_modal and self.victory_modal.active:
            self.victory_modal.handle_event(event)
            return
        if self.boss_preview and self.boss_preview.active:
            self.boss_preview.handle_key(event)

    def _update_camera(self):
        self.camera.follow(self.player.pos.x)

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
            next_location = cast(LocationName, nxt)
            modal = VictoryModal(
                title=title,
                lines=lines,
                on_continue=lambda: self.switch_location(next_location),
                localizer=self.localizer,
            )
            self.victory_modal = modal
            self.mode = "victory"
        else:
            self.finale.ensure_assets()
            self.finale.start(self.time_source.now_ms())
            self._pending_final_modal = (
                self.localizer.text("victory.title"),
                [
                    self.localizer.text("victory.final_boss"),
                    self.localizer.text("victory.mario_free"),
                    self.localizer.text("victory.celebrate"),
                ],
            )
            self.mode = "finale"

    def _start_boss_fight(self, boss: BossConfig) -> None:
        self.mode = "boss"
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
        if self.mode != "explore":
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
        if self.mode != "explore":
            return
        for position in self.collectible_system.collect(self.player.rect):
            self.fx_group.add(HitSpark(position, time_source=self.time_source))

    def _check_boss_gate(self):
        if self._boss_intro_shown or self.mode != "explore":
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
        self.mode = "explore"
        self._boss_intro_shown = False
        self._completion_reported = False
        self.current_boss = None
        self.boss_group.empty()
        self.fx_group.empty()
        self.projectiles.empty()
        self.victory_modal = None
        self._pending_final_modal = None
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
        self._update_camera()
        if self._collectible_hint_timer > 0.0:
            self._collectible_hint_timer = max(0.0, self._collectible_hint_timer - dt)

        if self.mode == "explore":
            self._handle_obstacle_collisions()
            self._collect_collectibles()
            self._check_boss_gate()
        elif self.mode == "boss":
            self.combat.update_boss_phase()
        elif self.mode == "finale":
            now = self.time_source.now_ms()
            if self.finale.ready_for_modal(now):
                if self._pending_final_modal and self.victory_modal is None:
                    title, lines = self._pending_final_modal
                    modal = VictoryModal(
                        title=title,
                        lines=lines,
                        on_continue=self._post_quit_event,
                        localizer=self.localizer,
                    )
                    modal.footer_text = self.localizer.text("victory.finish")
                    self.victory_modal = modal
                    self._pending_final_modal = None
                self.finale.reset()
                self.mode = "victory"

        if self.player.health <= 0:
            self.player.health = self.player.max_health
            self.switch_location(self.location)

    def _draw_boss_hp(self):
        boss = next(iter(self.boss_group), None)
        if not boss:
            return
        w, h = 320, 16
        offset_x = 72
        x = (self.screen.get_width() - w) // 2 + offset_x
        y = 18
        pygame.draw.rect(self.screen, (30, 30, 30), (x, y, w, h), border_radius=6)
        pygame.draw.rect(self.screen, (220, 220, 220), (x, y, w, h), 2, border_radius=6)
        ratio = boss.health / boss.max_health if boss.max_health > 0 else 0
        pygame.draw.rect(
            self.screen,
            (220, 70, 70),
            (x + 2, y + 2, int((w - 4) * ratio), h - 4),
            border_radius=5,
        )
        name_surf = self.font.render(boss.name, True, (240, 240, 240))
        self.screen.blit(name_surf, (x + (w - name_surf.get_width()) // 2, y + h + 6))

    def draw(self):
        if self.mode != "finale":
            self.bg.draw(self.screen, self.camera_x)
        else:
            self.finale.draw(self.screen)

        if self.mode == "explore":
            for sprite in self.obstacles:
                self.screen.blit(sprite.image, sprite.rect.move(-self.camera_x, 0))

            flag_x = int(self.boss_gate_x - self.camera_x)
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

        if self.mode != "finale":
            for item in self.collectibles:
                self.screen.blit(item.image, item.rect.move(-self.camera_x, 0))

        if self.mode == "boss":
            dim = pygame.Surface((WIDTH, self.screen.get_height()), pygame.SRCALPHA)
            dim.fill(BOSS_DIM_COLOR)
            self.screen.blit(dim, (0, 0))

        for pr in self.projectiles:
            self.screen.blit(pr.image, pr.rect.move(-self.camera_x, 0))

        for b in self.boss_group:
            b.draw(self.screen, self.camera_x)

        for fx in self.fx_group:
            fx.draw(self.screen, self.camera_x)

        if self.mode != "finale":
            self.player.draw(self.screen, self.camera_x)
            hud_progress = None
            icon = None
            if self.collectible_system.goal:
                hud_progress = self.collectible_system.progress
                icon = self.collectible_system.icon
            self.hud.draw(
                self.screen,
                self.player.health,
                self.player.max_health,
                collectibles=hud_progress,
                icon=icon,
            )
            if self.mode == "boss":
                self._draw_boss_hp()
            tip = self.font.render(
                self.localizer.text("game.help"), True, (230, 230, 230)
            )
            self.screen.blit(tip, (16, 12))
            if self._collectible_hint_timer > 0.0 and self._collectible_hint_text:
                hint = self.font.render(
                    self._collectible_hint_text, True, (255, 236, 210)
                )
                self.screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, 70))

        if self.victory_modal and self.victory_modal.active:
            self.victory_modal.draw(self.screen)
        elif self.boss_preview and not self.boss_preview.is_done():
            self.boss_preview.draw(self.screen)
