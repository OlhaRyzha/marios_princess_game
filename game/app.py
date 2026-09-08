import asyncio
import random
import sys
from collections.abc import Callable
from pathlib import Path

import pygame

from game.actions import MenuItem
from game.controller import ControllerEffect, GameController
from game.core.demo_scene import DemoScene
from game.data.bosses import BOSS_ROSTER
from game.data.locations import LocationName
from game.data.objectives import CONTROLS, OBJECTIVES
from game.data.start_menu import PAUSE_MENU_ITEMS, main_menu_items
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


def _sync_world_map(world_map: WorldMapScene, state: GameState[DemoScene]) -> None:
    world_map.set_progress(
        unlocked=state.progress.unlocked,
        completed=state.progress.completed,
    )


def _load_pending_scene(
    *,
    state: GameState[DemoScene],
    controller: GameController[DemoScene],
    world_map: WorldMapScene,
    scene_factory: SceneFactory,
    save_progress: Callable[[], None],
) -> None:
    if not state.scene_load_pending:
        return

    def handle_location_completed(location: LocationName) -> None:
        controller.complete_location(location)
        _sync_world_map(world_map, state)
        save_progress()

    def handle_game_finished() -> None:
        controller.finish_game()
        _sync_world_map(world_map, state)
        save_progress()

    state.scene = scene_factory.create_game_scene(
        state.progress.pending_location,
        on_location_completed=handle_location_completed,
        on_game_finished=handle_game_finished,
    )
    state.scene_load_pending = False


def _apply_effect(
    effect: ControllerEffect | None, state: GameState[DemoScene], menu: StartMenu
) -> None:
    if effect is ControllerEffect.START_SCENE:
        state.scene_load_pending = True
    elif effect is ControllerEffect.OPEN_CONTROLS:
        menu.open_controls()


def _sync_menu(
    state: GameState[DemoScene],
    menu: StartMenu,
    items: tuple[MenuItem, ...],
) -> None:
    if state.mode is GameMode.MENU:
        menu.set_items(items)
    elif state.mode is GameMode.MENU_PAUSE:
        menu.set_items(PAUSE_MENU_ITEMS)


def _update_gameplay(state: GameState[DemoScene], dt: float) -> None:
    if state.mode is not GameMode.GAME:
        state.time_accumulator = 0.0
        return
    if state.scene is None:
        state.time_accumulator = 0.0
        return

    active_scene = state.scene
    fixed_step = 1.0 / FPS
    accumulator = state.time_accumulator + dt
    while accumulator >= fixed_step:
        active_scene.update(fixed_step)
        accumulator -= fixed_step
    state.time_accumulator = accumulator
    if state.scene is active_scene:
        state.progress.pending_location = active_scene.location


def run_frame(
    *,
    clock: "pygame.time.Clock",
    dt_scale: float,
    menu: StartMenu,
    world_map: WorldMapScene,
    controller: GameController[DemoScene],
    input_adapter: InputAdapter[DemoScene],
    scene_factory: SceneFactory,
    renderer: FrameRenderer[DemoScene],
    save_progress: Callable[[], None],
    main_menu_items: tuple[MenuItem, ...],
) -> None:
    state = controller.state
    _load_pending_scene(
        state=state,
        controller=controller,
        world_map=world_map,
        scene_factory=scene_factory,
        save_progress=save_progress,
    )
    dt = clock.tick(FPS) / dt_scale
    dt = min(dt, 0.1)
    _sync_menu(state, menu, main_menu_items)
    for event in pygame.event.get():
        _apply_effect(input_adapter.route(event), state, menu)
    _sync_menu(state, menu, main_menu_items)
    _update_gameplay(state, dt)
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
        self._initialize_pygame()
        self._create_services(progress_store)
        self._create_navigation()
        self._create_adapters()

    def _initialize_pygame(self) -> None:
        """Initialize the display and frame clock."""
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()

    def _create_services(self, progress_store: ProgressStore | None) -> None:
        """Create runtime services and restore saved progress."""
        self.time_source = PygameTimeSource()
        self.input_source = PygameInputSource()
        self.rng = random.Random()
        self.audio_service = PygameAudioService()
        self.progress_store = progress_store or create_progress_store(
            is_web=self.is_web
        )
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

    def _create_navigation(self) -> None:
        """Create the main menu and world map."""
        self.menu = StartMenu(self.localizer)
        self.main_menu_items = main_menu_items(is_web=self.is_web)
        self.menu.set_items(self.main_menu_items)
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

    def _create_adapters(self) -> None:
        """Connect input routing and frame rendering."""
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
            main_menu_items=self.main_menu_items,
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
