import random
from collections.abc import Callable

import pygame

from game.data.locations import NEXT_LOCATION, LocationName
from game.gameplay.effects import ConfettiBurst
from game.i18n import Localizer
from game.scenes.finale import FinaleCinematic
from game.services.audio import AudioService
from game.state import SceneMode
from game.systems.time_source import TimeSource
from game.ui.ui_modal import VictoryModal
from game.utils.constants import FONT_SIZE, MUSIC_VICTORY


class DemoProgression:
    """Manage victory, location progression, and the final cinematic."""

    def __init__(
        self,
        *,
        screen: pygame.Surface,
        time_source: TimeSource,
        audio_service: AudioService,
        localizer: Localizer,
        rng: random.Random,
        on_location_completed: Callable[[LocationName], None] | None,
        on_game_finished: Callable[[], None] | None,
    ) -> None:
        self.screen = screen
        self.time_source = time_source
        self.audio_service = audio_service
        self.localizer = localizer
        self.rng = rng
        self.on_location_completed = on_location_completed
        self.on_game_finished = on_game_finished
        self.completion_reported = False
        self.finale = FinaleCinematic(duration_ms=3200, font_size=FONT_SIZE)

    def complete_boss(
        self,
        *,
        location: LocationName,
        effects: pygame.sprite.Group,
        on_continue: Callable[[LocationName], None],
    ) -> tuple[SceneMode, VictoryModal | None]:
        """Record a victory and prepare the next progression screen."""
        if not self.completion_reported and self.on_location_completed:
            self.completion_reported = True
            self.on_location_completed(location)

        self.audio_service.stop_music()
        self.audio_service.play_music(MUSIC_VICTORY, loop=False)
        effects.add(
            ConfettiBurst(
                self.screen.get_rect(),
                time_source=self.time_source,
                rng=self.rng,
            )
        )

        next_location = NEXT_LOCATION.get(location)
        if next_location:
            modal = VictoryModal(
                title=self.localizer.text("victory.title"),
                lines=[
                    self.localizer.text("victory.boss"),
                    "",
                    self.localizer.text("victory.next_goal"),
                    self.localizer.text(
                        "victory.next",
                        location=next_location.replace("_", " ").title(),
                    ),
                ],
                on_continue=lambda: on_continue(next_location),
                localizer=self.localizer,
            )
            return SceneMode.VICTORY, modal

        self.finale.ensure_assets()
        self.finale.start(self.time_source.now_ms())
        return SceneMode.FINALE, None

    def update_finale(self) -> None:
        """Finish the game after the final cinematic has played."""
        if not self.finale.ready_for_modal(self.time_source.now_ms()):
            return
        self.finale.reset()
        if self.on_game_finished:
            self.on_game_finished()

    def reset(self) -> None:
        """Reset progression state for a newly loaded location."""
        self.completion_reported = False
        self.finale.reset()
