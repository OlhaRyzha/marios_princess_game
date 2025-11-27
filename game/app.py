from __future__ import annotations
import asyncio
import sys
from typing import Mapping, TypedDict, cast
import pygame
from game.core import DemoScene
from game.data import BOSS_ROSTER
from game.data.locations import LOCATION_ORDER, LocationName
from game.data.objectives import CONTROLS, OBJECTIVES
from game.data.start_menu import MENU_ITEMS
from game.ui import StartMenu, WorldMapScene
from game.utils import FPS, HEIGHT, TITLE, WIDTH


class GameState(TypedDict):
    running: bool
    mode: str
    scene: DemoScene | None
    pending_location: LocationName
    progress_unlocked: set[LocationName]
    progress_completed: set[LocationName]
    audio_armed: bool
    time_accumulator: float


def _build_boss_thumbs() -> dict[str, str | None]:
    thumbs: dict[str, str | None] = {}
    for loc, lst in BOSS_ROSTER.items():
        thumbs[loc] = lst[0].get("img") if lst else None
    return thumbs


def _build_state(
    *,
    pending_location: LocationName,
    progress_unlocked: set[LocationName],
    progress_completed: set[LocationName],
    mode: str = "menu",
) -> GameState:
    return {
        "running": True,
        "mode": mode,
        "scene": None,
        "pending_location": pending_location,
        "progress_unlocked": progress_unlocked,
        "progress_completed": progress_completed,
        "audio_armed": False,
        "time_accumulator": 0.0,
    }


def run_frame(
    *,
    screen: pygame.Surface,
    clock: pygame.time.Clock,
    dt_scale: float,
    menu: StartMenu,
    world_map: WorldMapScene,
    state: GameState,
    is_web: bool,
) -> None:
    progress_unlocked: set[LocationName] = state["progress_unlocked"]
    progress_completed: set[LocationName] = state["progress_completed"]
    mode: str = state["mode"]
    scene: DemoScene | None = state["scene"]
    pending_location: LocationName = state["pending_location"]

    def update_world_map_progress() -> None:
        world_map.set_progress(unlocked=progress_unlocked, completed=progress_completed)

    def handle_location_completed(loc: LocationName) -> None:
        nonlocal pending_location
        if loc not in progress_completed:
            progress_completed.add(loc)
            try:
                idx = LOCATION_ORDER.index(loc)
            except ValueError:
                idx = -1
            if idx != -1 and idx + 1 < len(LOCATION_ORDER):
                next_loc = LOCATION_ORDER[idx + 1]
                progress_unlocked.add(next_loc)
                pending_location = next_loc
        update_world_map_progress()

    dt = clock.tick(FPS) / dt_scale
    dt = min(dt, 0.1)

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            state["running"] = False

        if is_web and (e.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN)):
            if not state["audio_armed"]:
                try:
                    pygame.mixer.init()
                except Exception:
                    pass
                state["audio_armed"] = True

        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_m and scene is not None:
                if mode == "game":
                    mode = "map_overlay"
                    state["mode"] = mode
                    continue
                elif mode == "map_overlay":
                    mode = "game"
                    state["mode"] = mode
                    continue

            if e.key == pygame.K_ESCAPE:
                if mode == "game":
                    mode = "menu_pause"
                    state["mode"] = mode
                    continue
                elif mode == "menu_pause":
                    mode = "game"
                    state["mode"] = mode
                    continue
                elif mode == "map":
                    mode = "menu"
                    state["mode"] = mode
                    continue
                elif mode == "map_overlay":
                    mode = "game"
                    state["mode"] = mode
                    continue

        if mode == "menu":
            menu.set_items(MENU_ITEMS)
            action = menu.handle_event(e)
            if action == "Почати гру":
                scene = DemoScene(
                    screen,
                    location=pending_location,
                    on_location_completed=handle_location_completed,
                )
                mode = "game"
            elif action == "Мапа світу":
                mode = "map"
            elif action == "Команди":
                menu.open_controls()
            elif action == "Вийти":
                state["running"] = False

        elif mode == "map":
            res = world_map.handle_event(e)
            if res:
                kind, payload = res
                if kind == "start" and payload:
                    pending_location = cast(LocationName, payload)
                    scene = DemoScene(
                        screen,
                        location=pending_location,
                        on_location_completed=handle_location_completed,
                    )
                    mode = "game"
                elif kind == "back":
                    mode = "menu"

        elif mode == "map_overlay":
            res = world_map.handle_event(e)
            if res:
                kind, payload = res
                if kind == "start" and payload:
                    pending_location = cast(LocationName, payload)
                    scene = DemoScene(
                        screen,
                        location=pending_location,
                        on_location_completed=handle_location_completed,
                    )
                    mode = "game"
                elif kind == "back":
                    mode = "game"

        elif mode == "menu_pause":
            menu.set_items(MENU_ITEMS)
            action = menu.handle_event(e)
            if action == "Продовжити гру":
                mode = "game"
            elif action == "Мапа світу":
                mode = "map_overlay"
            elif action == "Команди":
                menu.open_controls()
            elif action == "Вийти":
                state["running"] = False

        elif mode == "game":
            if scene is not None:
                scene.handle_event(e)

        state["scene"] = scene
        state["mode"] = mode
        state["pending_location"] = pending_location

    if mode == "menu":
        state["time_accumulator"] = 0.0
        menu.draw(screen)

    elif mode == "map":
        state["time_accumulator"] = 0.0
        world_map.draw(screen, overlay=False)

    elif mode == "game":
        if scene is not None:
            fixed_step = 1.0 / FPS
            accumulator = state["time_accumulator"] + dt
            while accumulator >= fixed_step:
                scene.update(fixed_step)
                accumulator -= fixed_step
            state["time_accumulator"] = accumulator
            scene.draw()
            state["pending_location"] = scene.location
        else:
            state["time_accumulator"] = 0.0

    elif mode == "map_overlay":
        state["time_accumulator"] = 0.0
        if scene is not None:
            scene.update(0.0)
            scene.draw()
            state["pending_location"] = scene.location
        world_map.draw(screen, overlay=True)

    elif mode == "menu_pause":
        state["time_accumulator"] = 0.0
        if scene is not None:
            scene.update(0.0)
            scene.draw()
        dim = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 110))
        screen.blit(dim, (0, 0))
        menu.draw(screen)

    pygame.display.flip()


class GameRuntime:
    def __init__(self, *, is_web: bool) -> None:
        self.is_web = is_web
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()

        self.progress_completed: set[LocationName] = set()
        self.progress_unlocked: set[LocationName] = {LOCATION_ORDER[0]}
        self.pending_location: LocationName = LOCATION_ORDER[0]

        self.menu = StartMenu()
        self.menu.set_controls(CONTROLS)
        mapped_objectives = cast(Mapping[LocationName, object], OBJECTIVES)
        self.world_map = WorldMapScene(
            objectives=mapped_objectives,
            boss_thumbs=_build_boss_thumbs(),
            unlocked=self.progress_unlocked,
            completed=self.progress_completed,
        )

        self.state: GameState = _build_state(
            pending_location=self.pending_location,
            progress_unlocked=self.progress_unlocked,
            progress_completed=self.progress_completed,
            mode="menu",
        )

        self.world_map.set_progress(
            unlocked=self.progress_unlocked, completed=self.progress_completed
        )

    def tick(self) -> None:
        run_frame(
            screen=self.screen,
            clock=self.clock,
            dt_scale=1000.0,
            menu=self.menu,
            world_map=self.world_map,
            state=self.state,
            is_web=self.is_web,
        )

    def run(self) -> None:
        while self.state["running"]:
            self.tick()
        self._shutdown()

    async def run_async(self) -> None:
        while self.state["running"]:
            self.tick()
            await asyncio.sleep(0)
        self._shutdown()

    def _shutdown(self) -> None:
        pygame.quit()


def run_game(is_web: bool | None = None) -> None:
    resolved_is_web = sys.platform == "emscripten" if is_web is None else is_web
    runtime = GameRuntime(is_web=resolved_is_web)
    if resolved_is_web:
        asyncio.run(runtime.run_async())
    else:
        runtime.run()
