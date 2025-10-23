from __future__ import annotations

from typing import Callable, Optional, cast

import pygame
from pygame.sprite import Group

from game.utils import (
    WIDTH,
    LEVEL_WIDTH,
    HELP_TEXT,
    FONT_SIZE,
    GROUND_Y,
    OBSTACLE_SCALE,
    DAMAGE_PER_HIT,
    MUSIC_BOSS,
    MUSIC_VICTORY,
    MUSIC_VOLUME,
    BOSS_DIM_COLOR,
    MUSIC_LEVEL,
)
from game.utils.fonts import load_font
from game.utils.images import scale_to_height
from game.core.background import ParallaxBackground
from game.core.player import Princess
from game.ui.hud import HealthHUD
from game.data import BOSS_ROSTER, COLLECTIBLE_SETS, LocationName, NEXT_LOCATION
from game.ui.boss_preview import BossPreview
from game.core.boss_actor import BossActor
from game.core.effects import ConfettiBurst, HitSpark
from game.ui.ui_modal import VictoryModal
from game.core.combat import CombatSystem
from game.core.collision import MaskedSprite, collide_mask
from game.core.obstacle_factory import build_obstacles, boss_gate_position
from game.core.finale import FinaleCinematic
from game.core.collectible import Collectible


class DemoScene:
    def __init__(
        self,
        screen: pygame.Surface,
        location: LocationName = "sunny_meadows",
        *,
        on_location_completed: Callable[[LocationName], None] | None = None,
    ):
        self.screen = screen
        self.bg = ParallaxBackground(location)

        self.START_X = 240
        self.player: Princess = Princess((self.START_X, GROUND_Y))

        self.all_sprites: Group = Group()
        self.obstacles: Group = Group()
        self.boss_group: Group = Group()
        self.fx_group: Group = Group()
        self.projectiles: Group = Group()
        self.collectibles: Group = Group()
        self.all_sprites.add(self.player)

        self.combat = CombatSystem(
            self.player,
            self.boss_group,
            self.projectiles,
            self.fx_group,
            on_boss_defeated=self._on_boss_victory,
        )

        self.location: LocationName = location
        self.boss_gate_x = 0
        self._boss_trigger_rect = pygame.Rect(0, 0, 48, self.screen.get_height())

        self.camera_x = 0.0
        self.font = load_font(FONT_SIZE)
        self.tip = self.font.render(HELP_TEXT, True, (230, 230, 230))
        self.hud = HealthHUD()

        self.mode = "explore"
        self.current_boss: dict | None = None
        self._completion_reported = False
        self._on_location_completed = on_location_completed
        self.boss_preview = BossPreview(self.font, on_select=self._on_boss_selected)
        self._boss_intro_shown = False

        self.victory_modal: VictoryModal | None = None
        self.finale = FinaleCinematic(duration_ms=3200, font_size=FONT_SIZE)
        self._pending_final_modal: Optional[tuple[str, list[str]]] = None
        self.collectible_goal = 0
        self.collectibles_collected = 0
        self.collectible_icon: Optional[pygame.Surface] = None
        self.collectible_label: str = ""
        self.collectible_hint_line: str = ""
        self.collectible_progress_text: str = ""
        self._collectible_hint_timer: float = 0.0
        self._collectible_hint_text: str = ""

        self._load_obstacles(location)

        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init()
            except Exception:
                pass
        self._stop_music()
        self._play_music(MUSIC_LEVEL, loop=True)

    def _load_obstacles(self, location: LocationName):

        old_obstacles = tuple(self.obstacles.sprites())
        if old_obstacles:
            self.all_sprites.remove(*old_obstacles)
        self.obstacles.empty()

        new_obstacles, max_right = build_obstacles(
            location=location,
            start_x=self.START_X,
            scale=OBSTACLE_SCALE,
        )
        if new_obstacles:
            self.obstacles.add(*new_obstacles)
            self.all_sprites.add(*new_obstacles)

        self._spawn_collectibles(location)
        self.boss_gate_x = boss_gate_position(max_right)
        self._boss_trigger_rect = pygame.Rect(
            self.boss_gate_x, 0, 48, self.screen.get_height()
        )

    def _spawn_collectibles(self, location: LocationName) -> None:
        for sprite in self.collectibles.sprites():
            sprite.kill()
        self.collectibles.empty()
        self.collectibles_collected = 0
        self.collectible_goal = 0
        self.collectible_icon = None
        self.collectible_label = ""
        self.collectible_hint_line = ""
        self.collectible_progress_text = ""
        self._collectible_hint_text = ""
        setup = COLLECTIBLE_SETS.get(location)
        if not setup:
            return

        world_surface: Optional[pygame.Surface] = None
        icon_surface: Optional[pygame.Surface] = None
        if setup.image_path:
            try:
                raw = pygame.image.load(setup.image_path).convert_alpha()
                world_surface = scale_to_height(raw, setup.world_height)
                icon_surface = scale_to_height(raw, setup.icon_height)
            except Exception:
                world_surface = None
                icon_surface = None

        for pos in setup.positions:
            item = Collectible(setup.kind, pos, surface=world_surface)
            self.collectibles.add(item)

        self.collectible_goal = len(setup.positions)
        if icon_surface is not None:
            self.collectible_icon = icon_surface.copy()
        else:
            self.collectible_icon = Collectible.icon(setup.kind, size=26)
        self.collectible_label = setup.label
        self.collectible_hint_line = setup.hint
        self._update_collectible_progress()

    def _update_collectible_progress(self) -> None:
        if self.collectible_goal:
            self.collectible_progress_text = (
                f"{self.collectible_label}: "
                f"{self.collectibles_collected}/{self.collectible_goal}"
            )
        else:
            self.collectible_progress_text = ""

    def handle_event(self, e: pygame.event.Event):
        if self.victory_modal and self.victory_modal.active:
            self.victory_modal.handle_event(e)
            return
        if self.boss_preview and self.boss_preview.active:
            self.boss_preview.handle_key(e)

    def _update_camera(self):
        self.camera_x = max(
            0.0, min(self.player.pos.x - WIDTH * 0.5, LEVEL_WIDTH - WIDTH)
        )

    def _play_music(self, path: str, *, loop: bool = True):
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(MUSIC_VOLUME)
            pygame.mixer.music.play(-1 if loop else 0)
        except Exception:
            pass

    def _stop_music(self):
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass

    def _sync_player_rect(self) -> None:
        self.player.rect.midbottom = (int(self.player.pos.x), int(self.player.pos.y))

    def _on_boss_selected(self, boss: dict):
        self.current_boss = boss
        self._start_boss_fight(boss)

    def _on_boss_victory(self) -> None:
        if not self._completion_reported and self._on_location_completed:
            self._completion_reported = True
            self._on_location_completed(self.location)

        self.boss_group.empty()
        self.projectiles.empty()
        self._stop_music()
        self._play_music(MUSIC_VICTORY, loop=False)
        self.fx_group.add(ConfettiBurst(self.screen.get_rect()))

        nxt = NEXT_LOCATION.get(self.location)
        if nxt:
            title = "You win!"
            lines = [
                "Ти здолала боса!",
                "",
                "Ціль наступного рівня: подолати перепони та перемогти боса, щоб врятувати Маріо.",
                f"Далі: {nxt.replace('_', ' ').title()}",
            ]
            next_location = cast(LocationName, nxt)
            modal = VictoryModal(
                title=title,
                lines=lines,
                on_continue=lambda: self.switch_location(next_location),
            )
            self.victory_modal = modal
            self.mode = "victory"
        else:
            self.finale.ensure_assets()
            self.finale.start(pygame.time.get_ticks())
            self._pending_final_modal = (
                "You win!",
                [
                    "Ти здолала фінального боса!",
                    "Кришталева клітка розсипається — Маріо вільний.",
                    "Свято, конфеті і нові пригоди попереду!",
                ],
            )
            self.mode = "finale"

    def _start_boss_fight(self, boss: dict):
        self.mode = "boss"
        self._stop_music()
        self._play_music(MUSIC_BOSS, loop=True)

        view_left = self.camera_x
        view_right = self.camera_x + WIDTH

        left_margin = 120
        self.player.pos.x = max(
            view_left + left_margin, min(self.player.pos.x, view_right - left_margin)
        )
        self._sync_player_rect()

        pre_x = max(120, min(view_right - 140, LEVEL_WIDTH - 120))
        boss_actor = BossActor(name=boss["name"], image_path=boss["img"], x=int(pre_x))

        desired_right = view_right - 120
        boss_actor.rect.right = int(desired_right)

        min_left_visible = view_left + 40
        max_right_visible = view_right - 40
        if boss_actor.rect.left < min_left_visible:
            boss_actor.rect.left = int(min_left_visible)
        if boss_actor.rect.right > max_right_visible:
            boss_actor.rect.right = int(max_right_visible)

        min_gap = 140
        if self.player.rect.right > boss_actor.rect.left - min_gap:
            new_px: float = boss_actor.rect.left - min_gap - self.player.rect.width // 2
            new_px = max(view_left + left_margin, new_px)
            self.player.pos.x = new_px
            self._sync_player_rect()

        min_cam = max(0, boss_actor.rect.right - (WIDTH - 80))
        max_cam = min(LEVEL_WIDTH - WIDTH, self.player.pos.x - 80)
        if min_cam <= max_cam:
            self.camera_x = max(min_cam, min(self.camera_x, max_cam))
        else:
            self.camera_x = max(
                0, min(boss_actor.rect.centerx - (WIDTH - 140), LEVEL_WIDTH - WIDTH)
            )

        self.combat.start_boss(boss_actor)

    def _handle_obstacle_collisions(self):
        if self.mode != "explore":
            return
        hits = [
            obstacle
            for obstacle in self.obstacles
            if collide_mask(
                cast(MaskedSprite, self.player), cast(MaskedSprite, obstacle)
            )
        ]
        if hits and self.player.can_take_damage():
            self.player.take_damage(DAMAGE_PER_HIT)
            self.player.pos.x += -18 if self.player.dir > 0 else 18
            self.player.rect.x = int(self.player.pos.x)

    def _collect_collectibles(self):
        if self.mode != "explore" or not self.collectible_goal:
            return
        hits = pygame.sprite.spritecollide(self.player, self.collectibles, dokill=True)
        if hits:
            for item in hits:
                self.fx_group.add(HitSpark(item.rect.center))
            self.collectibles_collected += len(hits)
            if self.collectibles_collected > self.collectible_goal:
                self.collectibles_collected = self.collectible_goal
            self._update_collectible_progress()

    def _check_boss_gate(self):
        if self._boss_intro_shown or self.mode != "explore":
            return
        if self.player.rect.right >= self._boss_trigger_rect.left:
            if (
                self.collectible_goal
                and self.collectibles_collected < self.collectible_goal
            ):
                self._collectible_hint_text = (
                    f"{self.collectible_hint_line} "
                    f"({self.collectibles_collected}/{self.collectible_goal})"
                )
                self._collectible_hint_timer = 2.6
                return
            bosses = BOSS_ROSTER.get(self.location, [])
            if bosses:
                self.boss_preview.open(bosses)
            self._boss_intro_shown = True

    def switch_location(self, location: LocationName):
        self.bg.set_location(location)
        self.location = location
        self._load_obstacles(location)

        self.player.pos.update(self.START_X, GROUND_Y)
        self._sync_player_rect()

        self.camera_x = 0
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
        self._stop_music()
        self._play_music(MUSIC_LEVEL, loop=True)

    def update(self, dt: float):
        keys = pygame.key.get_pressed()
        self.all_sprites.update(dt, keys)
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
            now = pygame.time.get_ticks()
            if self.finale.ready_for_modal(now):
                if self._pending_final_modal and self.victory_modal is None:
                    title, lines = self._pending_final_modal
                    modal = VictoryModal(
                        title=title,
                        lines=lines,
                        on_continue=lambda: pygame.event.post(
                            pygame.event.Event(pygame.QUIT)
                        ),
                    )
                    if hasattr(modal, "footer_text"):
                        try:
                            modal.footer_text = "Натисни Enter, щоб завершити гру"
                        except Exception:
                            pass
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
            if self.collectible_goal:
                hud_progress = (
                    self.collectibles_collected,
                    self.collectible_goal,
                )
                icon = self.collectible_icon
            self.hud.draw(
                self.screen,
                self.player.health,
                self.player.max_health,
                collectibles=hud_progress,
                icon=icon,
            )
            if self.mode == "boss":
                self._draw_boss_hp()
            self.screen.blit(self.tip, (16, 12))
            if self._collectible_hint_timer > 0.0 and self._collectible_hint_text:
                hint = self.font.render(
                    self._collectible_hint_text, True, (255, 236, 210)
                )
                self.screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, 70))

        if self.victory_modal and self.victory_modal.active:
            self.victory_modal.draw(self.screen)
        elif self.boss_preview and not self.boss_preview.is_done():
            self.boss_preview.draw(self.screen)
