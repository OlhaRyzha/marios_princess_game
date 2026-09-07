import asyncio
import random
import sys
from collections.abc import Callable
from pathlib import Path

import pygame

from game.controller import ControllerEffect, GameController
from game.core.demo_scene import DemoScene
from game.data.bosses import BOSS_ROSTER
from game.data.locations import LocationName
from game.data.objectives import CONTROLS, OBJECTIVES
from game.data.start_menu import MAIN_MENU_ITEMS, PAUSE_MENU_ITEMS
from game.frame_renderer import FrameRenderer
from game.i18n import Localizer
from game.input_adapter import InputAdapter
from game.scene_factory import SceneFactory
from game.services.audio import PygameAudioService
from game.services.progress import (
    ProgressSnapshot,
    ProgressStore,
    create_progress_store,
)
from game.state import GameMode, GameState
from game.systems.input_state import PygameInputSource
from game.systems.time_source import PygameTimeSource
from game.ui.start_menu import StartMenu
from game.ui.world_map import WorldMapScene
from game.utils.constants import FPS, HEIGHT, TITLE, WIDTH


def _build_boss_thumbs() -> dict[str, Path | None]:
    thumbs: dict[str, Path | None] = {}
    for loc, lst in BOSS_ROSTER.items():
        thumbs[loc] = lst[0].image_path if lst else None
    return thumbs


def run_frame(
    *,
    clock: pygame.time.Clock,
    dt_scale: float,
    menu: StartMenu,
    world_map: WorldMapScene,
    controller: GameController[DemoScene],
    input_adapter: InputAdapter[DemoScene],
    scene_factory: SceneFactory,
    renderer: FrameRenderer[DemoScene],
    save_progress: Callable[[], None],
) -> None:
    state = controller.state

    def update_world_map_progress() -> None:
        world_map.set_progress(
            unlocked=state.progress.unlocked,
            completed=state.progress.completed,
        )

    def handle_location_completed(loc: LocationName) -> None:
        controller.complete_location(loc)
        update_world_map_progress()
        save_progress()

    def start_scene() -> None:
        state.scene = scene_factory.create_game_scene(
            state.progress.pending_location,
            on_location_completed=handle_location_completed,
        )

    def apply_effect(effect: ControllerEffect | None) -> None:
        if effect is ControllerEffect.START_SCENE:
            state.scene_load_pending = True
        elif effect is ControllerEffect.OPEN_CONTROLS:
            menu.open_controls()

    def sync_menu_items() -> None:
        if state.mode is GameMode.MENU:
            menu.set_items(MAIN_MENU_ITEMS)
        elif state.mode is GameMode.MENU_PAUSE:
            menu.set_items(PAUSE_MENU_ITEMS)

    if state.scene_load_pending:
        start_scene()
        state.scene_load_pending = False

    dt = clock.tick(FPS) / dt_scale
    dt = min(dt, 0.1)
    sync_menu_items()

    for e in pygame.event.get():
        apply_effect(input_adapter.route(e))

    sync_menu_items()

    if state.mode is GameMode.GAME:
        if state.scene is not None:
            fixed_step = 1.0 / FPS
            accumulator = state.time_accumulator + dt
            while accumulator >= fixed_step:
                state.scene.update(fixed_step)
                accumulator -= fixed_step
            state.time_accumulator = accumulator
            state.progress.pending_location = state.scene.location
        else:
            state.time_accumulator = 0.0
    else:
        state.time_accumulator = 0.0

    if state.scene_load_pending:
        renderer.draw_loading()
    else:
        renderer.draw(state)


class GameRuntime:
    def __init__(
        self,
        *,
        is_web: bool,
        progress_store: ProgressStore | None = None,
    ) -> None:
        self.is_web = is_web
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.time_source = PygameTimeSource()
        self.input_source = PygameInputSource()
        self.rng = random.Random()
        self.audio_service = PygameAudioService()
        self.progress_store = progress_store or create_progress_store(is_web=is_web)
        self.localizer = Localizer()
        self.scene_factory = SceneFactory(
            screen=self.screen,
            time_source=self.time_source,
            input_source=self.input_source,
            rng=self.rng,
            audio_service=self.audio_service,
            localizer=self.localizer,
        )

        self.state = GameState[DemoScene]()
        self._load_progress()
        self.controller = GameController(self.state)

        self.menu = StartMenu(self.localizer)
        self.menu.set_controls(CONTROLS)
        self.world_map = WorldMapScene(
            objectives=OBJECTIVES,
            boss_thumbs=_build_boss_thumbs(),
            unlocked=self.state.progress.unlocked,
            completed=self.state.progress.completed,
            time_source=self.time_source,
            rng=self.rng,
            localizer=self.localizer,
        )

        self.world_map.set_progress(
            unlocked=self.state.progress.unlocked,
            completed=self.state.progress.completed,
        )
        self.input_adapter = InputAdapter(
            controller=self.controller,
            menu=self.menu,
            world_map=self.world_map,
            audio_service=self.audio_service,
            input_source=self.input_source,
            localizer=self.localizer,
            is_web=self.is_web,
            toggle_fullscreen=self._toggle_fullscreen,
        )
        self.renderer = FrameRenderer[DemoScene](
            screen=self.screen,
            menu=self.menu,
            world_map=self.world_map,
        )

    def _toggle_fullscreen(self) -> None:
        """Toggle desktop fullscreen when the display driver supports it."""
        if self.is_web:
            return
        try:
            pygame.display.toggle_fullscreen()
        except pygame.error:
            return

    def tick(self) -> None:
        run_frame(
            clock=self.clock,
            dt_scale=1000.0,
            menu=self.menu,
            world_map=self.world_map,
            controller=self.controller,
            input_adapter=self.input_adapter,
            scene_factory=self.scene_factory,
            renderer=self.renderer,
            save_progress=self.save_progress,
        )

    def _load_progress(self) -> None:
        snapshot = self.progress_store.load()
        if snapshot is None:
            return
        self.state.progress.unlocked = set(snapshot.unlocked)
        self.state.progress.completed = set(snapshot.completed)
        self.state.progress.pending_location = snapshot.pending_location

    def save_progress(self) -> None:
        progress = self.state.progress
        self.progress_store.save(
            ProgressSnapshot(
                unlocked=frozenset(progress.unlocked),
                completed=frozenset(progress.completed),
                pending_location=progress.pending_location,
            )
        )

    def run(self) -> None:
        while self.state.running:
            self.tick()
        self._shutdown()

    async def run_async(self) -> None:
        while self.state.running:
            self.tick()
            await asyncio.sleep(0)
        self._shutdown()

    def _shutdown(self) -> None:
        self.save_progress()
        self.audio_service.stop_music()
        pygame.quit()


def run_game(is_web: bool | None = None) -> None:
    resolved_is_web = sys.platform == "emscripten" if is_web is None else is_web
    runtime = GameRuntime(is_web=resolved_is_web)
    if resolved_is_web:
        asyncio.run(runtime.run_async())
    else:
        runtime.run()
