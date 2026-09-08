import pygame

from game.systems.animation import Animation
from game.systems.input_state import InputState
from game.systems.time_source import TimeSource
from game.utils.assets import load_sequence
from game.utils.constants import (
    AIR_ACCEL,
    AIR_FRICTION,
    AIR_MAX_SPEED,
    CRAWL_SPEED,
    CROUCH_SCALE,
    DAMAGE_COOLDOWN_MS,
    DIR_BUFFER_MS,
    GRAVITY,
    GROUND_Y,
    JUMP_V,
    LEVEL_WIDTH,
    MAX_HEALTH,
    SPEED_RUN,
    SPEED_WALK,
    TARGET_H,
    WIDTH,
)


class Princess(pygame.sprite.Sprite):
    def __init__(
        self,
        pos: tuple[int, int],
        *groups: "pygame.sprite.AbstractGroup",
        time_source: TimeSource,
    ) -> None:
        super().__init__(*groups)
        self.time_source = time_source

        self.anims: dict[str, Animation] = {
            "idle": Animation(
                load_sequence("idle", "princess_idle_", TARGET_H), fps=6, loop=True
            ),
            "walk": Animation(
                load_sequence("walk", "princess_walk_", TARGET_H), fps=10, loop=True
            ),
            "run": Animation(
                load_sequence("run", "princess_run_", TARGET_H), fps=12, loop=True
            ),
            "jump": Animation(
                load_sequence("jump", "princess_jump_", TARGET_H), fps=10, loop=False
            ),
            "fall": Animation(
                load_sequence("fall", "princess_fall_", TARGET_H), fps=10, loop=True
            ),
            "cry": Animation(
                load_sequence("cry", "princess_cry_", TARGET_H), fps=10, loop=False
            ),
            "attack": Animation(
                load_sequence("attack", "princess_attack_", TARGET_H),
                fps=12,
                loop=False,
            ),
            "hurt": Animation(
                load_sequence("hit", "princess_hurt_", TARGET_H), fps=8, loop=False
            ),
            "celebrate": Animation(
                load_sequence("celebrate", "princess_celebrate_", TARGET_H),
                fps=8,
                loop=True,
            ),
        }
        self.anims["crouch"] = self._build_crouch_from_fall()
        self.anims["crawl"] = self._build_crawl_from_fall()

        self.state = "idle"
        self.dir = 1
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(0, 0)
        self.on_ground = False
        self.state_timer = 0.0
        self.crouched = False

        self.image: pygame.Surface = self.anims["idle"].image()
        self.rect: pygame.Rect = self.image.get_rect(midbottom=(self.pos.x, self.pos.y))
        self.mask: pygame.mask.Mask = pygame.mask.from_surface(self.image)

        self.max_health = MAX_HEALTH
        self.health = MAX_HEALTH
        self._last_hit_ms = -10_000

        self._last_dir_input = 0
        self._last_dir_time_ms = -10_000

    def _build_crouch_from_fall(self) -> Animation:
        frames = load_sequence("fall", "princess_fall_", TARGET_H)
        if not frames:
            frames = [self.anims["idle"].image()]
        base = frames[0]
        w, h = base.get_size()
        ch = max(1, int(h * CROUCH_SCALE))
        crouch_img = pygame.transform.smoothscale(base, (w, ch))
        return Animation([crouch_img], fps=1, loop=True)

    def _build_crawl_from_fall(self) -> Animation:
        frames = load_sequence("fall", "princess_fall_", TARGET_H)
        out: list[pygame.Surface] = []
        if not frames:
            frames = [self.anims["idle"].image()]
        take = min(4, len(frames))
        for i in range(take):
            f = frames[i]
            w, h = f.get_size()
            ch = max(1, int(h * CROUCH_SCALE))
            out.append(pygame.transform.smoothscale(f, (w, ch)))
        if not out:
            base = frames[0]
            w, h = base.get_size()
            ch = max(1, int(h * CROUCH_SCALE))
            out.append(pygame.transform.smoothscale(base, (w, ch)))
        return Animation(out, fps=8, loop=True)

    def can_take_damage(self) -> bool:
        return (self.time_source.now_ms() - self._last_hit_ms) >= DAMAGE_COOLDOWN_MS

    def take_damage(self, amount: int = 1):
        if not self.can_take_damage():
            return
        self.health = max(0, self.health - amount)
        self._last_hit_ms = self.time_source.now_ms()
        self.set_state("hurt", timer=0.35)

    def set_state(self, s: str, timer: float = 0.0):
        if s != self.state:
            self.state = s
            self.state_timer = timer
            self.anims[s].reset()
        else:
            self.state_timer = max(self.state_timer, timer)

    def _remember_dir(self, d: int):
        if d != 0:
            self._last_dir_input = 1 if d > 0 else -1
            self._last_dir_time_ms = self.time_source.now_ms()

    def _dir_from_buffer(self) -> int:
        if self.time_source.now_ms() - self._last_dir_time_ms <= DIR_BUFFER_MS:
            return self._last_dir_input
        return 0

    def _handle_input(self, input_state: InputState) -> None:
        moving = False
        running = input_state.run
        speed = SPEED_RUN if running else SPEED_WALK

        self.crouched = input_state.down
        if self.crouched:
            speed = speed * CRAWL_SPEED

        left = input_state.left
        right = input_state.right

        if left:
            self.vel.x = -speed if self.on_ground else self.vel.x
            self.dir = -1
            moving = True
            self._remember_dir(-1)
        elif right:
            self.vel.x = speed if self.on_ground else self.vel.x
            self.dir = 1
            moving = True
            self._remember_dir(1)
        else:
            if self.on_ground:
                self.vel.x = 0

        if input_state.attack:
            self.set_state("attack", timer=0.35)
        elif input_state.celebrate:
            self.set_state("celebrate", timer=0.8)
        elif input_state.hurt:
            self.set_state("hurt", timer=0.5)
        elif input_state.cry:
            self.set_state("cry", timer=0.5)

        if input_state.jump and self.on_ground and not self.crouched:
            self.vel.y = JUMP_V
            if not (left or right):
                self.vel.x = 0
            self.on_ground = False
            self.set_state("jump")

        if self.on_ground and self.state not in ("attack", "hurt", "cry"):
            if self.crouched:
                self.set_state("crawl" if moving else "crouch")
            else:
                self.set_state(
                    "run" if (moving and running) else "walk" if moving else "idle"
                )

        if not self.on_ground and not self.crouched:
            if left and not right:
                self.vel.x -= AIR_ACCEL
            elif right and not left:
                self.vel.x += AIR_ACCEL
            else:
                if self.vel.x > 0:
                    self.vel.x = max(0, self.vel.x - AIR_FRICTION)
                elif self.vel.x < 0:
                    self.vel.x = min(0, self.vel.x + AIR_FRICTION)

            if self.vel.x > AIR_MAX_SPEED:
                self.vel.x = AIR_MAX_SPEED
            elif self.vel.x < -AIR_MAX_SPEED:
                self.vel.x = -AIR_MAX_SPEED

    def _physics(self):
        self.vel.y += GRAVITY
        self.pos += self.vel

        if self.pos.y >= GROUND_Y:
            self.pos.y = GROUND_Y
            if not self.on_ground:
                self.on_ground = True
                if self.state in ("jump", "fall"):
                    self.set_state("crouch" if self.crouched else "idle")
            self.vel.y = 0
        else:
            self.on_ground = False
            if self.vel.y > 0 and self.state == "jump":
                self.set_state("fall")

        half_w = max(1, self.image.get_width() // 2)
        world_w = LEVEL_WIDTH or WIDTH
        self.pos.x = max(half_w, min(self.pos.x, world_w - half_w))

        self.rect = self.image.get_rect(midbottom=(self.pos.x, self.pos.y))
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt: float, input_state: InputState) -> None:
        if (
            self.state in ("attack", "hurt", "cry", "celebrate")
            and self.state_timer > 0
        ):
            self.state_timer -= dt
            if self.state_timer <= 0:
                if self.on_ground:
                    self.set_state("crouch" if self.crouched else "idle")
                else:
                    self.set_state("fall")

        if self.state not in ("attack", "hurt", "cry", "celebrate"):
            self._handle_input(input_state)

        self._physics()

        self.anims[self.state].update(dt)
        img = self.anims[self.state].image()
        if self.dir == -1:
            img = pygame.transform.flip(img, True, False)
        self.image = img
        self.rect = self.image.get_rect(midbottom=(self.pos.x, self.pos.y))
        self.mask = pygame.mask.from_surface(self.image)

    def draw(self, surface: "pygame.Surface", camera_x: float):
        surface.blit(self.image, self.rect.move(-camera_x, 0))
