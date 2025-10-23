from __future__ import annotations

from pathlib import Path


WIDTH, HEIGHT = 1280, 720
FPS = 60
TITLE = "Mario’s Princess — demo"


GRAVITY = 0.8
SPEED_WALK = 3.0
SPEED_RUN = 5.0
JUMP_V = -18.0
JUMP_PUSH_X = 14.0


LEVEL_WIDTH = 4000
GROUND_STRIP_H = 90
GROUND_Y = HEIGHT - 72
TARGET_H = 220


FONT_NAME = "arialunicode"
FONT_SIZE = 22
HELP_TEXT = "←/→ move, space — jump, ↓ — crouch, j — attack"


BASE_DIR = Path(__file__).resolve().parents[2]
ASSETS_DIR = str(BASE_DIR / "assets")
SPRITES_DIR = f"{ASSETS_DIR}/princess"
BACKGROUNDS_DIR = f"{ASSETS_DIR}/backgrounds"
AUDIO_DIR = str(Path(ASSETS_DIR) / "audio")
MAP_DIR = str(Path(ASSETS_DIR) / "map")


PARALLAX_PRESETS = {
    "sunny_meadows": {
        "far": {"speed": 0.20},
        "mid": {"speed": 0.45},
        "fore": {"speed": 0.70},
    },
    "mushroom_woods": {
        "far": {"speed": 0.18},
        "mid": {"speed": 0.40},
        "fore": {"speed": 0.65},
    },
    "crystal_caves": {
        "far": {"speed": 0.16},
        "mid": {"speed": 0.38},
        "fore": {"speed": 0.62},
    },
}


PARALLAX_LAYOUT = {
    "sunny_meadows": {
        "far": {"target_h": 560, "above": -90, "show_top": None},
        "mid": {"target_h": 360, "above": -20, "show_top": None},
        "fore": {"target_h": 220, "above": -40, "show_top": None},
    },
    "mushroom_woods": {
        "far": {"target_h": 520, "above": -110, "show_top": None},
        "mid": {"target_h": 380, "above": -50, "show_top": None},
        "fore": {"target_h": 260, "above": -44, "show_top": 240},
    },
    "crystal_caves": {
        "far": {"target_h": 520, "above": -120, "tile": "mirror"},
        "mid": {"target_h": 360, "above": -48, "tile": "mirror"},
        "fore": {"target_h": 240, "above": -42, "tile": "mirror", "show_top": 210},
    },
}


GROUND_THEMES = {
    "sunny_meadows": {
        "soil_base": (182, 130, 78),
        "grass_top": (124, 184, 62),
        "grass_edge": (84, 140, 40),
        "stone_a": (150, 110, 70),
        "stone_b": (165, 120, 75),
    },
    "mushroom_woods": {
        "soil_base": (72, 52, 98),
        "grass_top": (120, 100, 160),
        "grass_edge": (90, 75, 130),
        "stone_a": (96, 78, 128),
        "stone_b": (112, 90, 148),
    },
    "crystal_caves": {
        "soil_base": (40, 52, 78),
        "grass_top": (96, 140, 180),
        "grass_edge": (68, 110, 150),
        "stone_a": (70, 96, 128),
        "stone_b": (86, 118, 156),
    },
}


OBSTACLE_SCALE = 0.1


MAX_HEALTH = 5
DAMAGE_PER_HIT = 1
DAMAGE_COOLDOWN_MS = 800
CROUCH_SCALE = 0.65
CRAWL_SPEED = 0.85
DIR_BUFFER_MS = 120
AIR_ACCEL = 0.35
AIR_MAX_SPEED = 6.5
AIR_FRICTION = 0.015
BOSS_SCALE = 0.32
BOSS_MAX_HEALTH = 6
BOSS_SPEED = 1.8
BOSS_JUMP_V = -12.0
BOSS_HIT_COOLDOWN_MS = 280
ATTACK_DAMAGE = 1
ATTACK_HIT_COOLDOWN_MS = 380
HIT_SPARK_TIME_MS = 220

MUSIC_LEVEL = "assets/audio/level_theme.mp3"
MUSIC_BOSS = "assets/audio/boss_theme.mp3"
MUSIC_VICTORY = "assets/audio/victory_theme.mp3"
MUSIC_VOLUME = 0.6

CONFETTI_TIME_MS = 1600
BOSS_DIM_COLOR = (10, 14, 26, 160)
VICTORY_DIM_COLOR = (10, 14, 26, 120)

__all__ = [name for name in globals() if name.isupper()]
