from dataclasses import dataclass

from game.core.boss_actor import BossActor
from game.core.player import Princess
from game.data.bosses import BossConfig
from game.systems.time_source import TimeSource


@dataclass(frozen=True, slots=True)
class BossArena:
    """Place the player and boss inside the current camera viewport."""

    viewport_width: int
    level_width: int
    left_margin: int = 120

    def arrange(
        self,
        *,
        player: Princess,
        boss: BossConfig,
        camera_x: float,
        time_source: TimeSource,
    ) -> tuple[BossActor, float]:
        view_left = camera_x
        view_right = camera_x + self.viewport_width
        player.pos.x = max(
            view_left + self.left_margin,
            min(player.pos.x, view_right - self.left_margin),
        )
        player.rect.midbottom = (int(player.pos.x), int(player.pos.y))

        spawn_x = max(120, min(view_right - 140, self.level_width - 120))
        actor = BossActor(
            name=boss.name,
            image_path=boss.image_path,
            x=int(spawn_x),
            time_source=time_source,
        )
        actor.rect.right = int(view_right - 120)
        actor.rect.left = max(actor.rect.left, int(view_left + 40))
        actor.rect.right = min(actor.rect.right, int(view_right - 40))

        minimum_gap = 140
        if player.rect.right > actor.rect.left - minimum_gap:
            player.pos.x = max(
                view_left + self.left_margin,
                actor.rect.left - minimum_gap - player.rect.width // 2,
            )
            player.rect.midbottom = (int(player.pos.x), int(player.pos.y))

        minimum_camera = max(0, actor.rect.right - (self.viewport_width - 80))
        maximum_camera = min(self.level_width - self.viewport_width, player.pos.x - 80)
        if minimum_camera <= maximum_camera:
            camera_x = max(minimum_camera, min(camera_x, maximum_camera))
        else:
            camera_x = max(
                0,
                min(
                    actor.rect.centerx - (self.viewport_width - 140),
                    self.level_width - self.viewport_width,
                ),
            )
        return actor, camera_x
