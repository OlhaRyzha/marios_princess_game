from game.data.bosses import BOSS_ROSTER, BossConfig
from game.data.locations import LOCATION_ORDER


def test_every_location_has_valid_boss_configs() -> None:
    assert set(BOSS_ROSTER) == set(LOCATION_ORDER)

    for bosses in BOSS_ROSTER.values():
        assert bosses
        assert all(isinstance(boss, BossConfig) for boss in bosses)
        assert all(boss.name for boss in bosses)
        assert all(boss.image_path.is_absolute() for boss in bosses)
        assert all(boss.image_path.is_file() for boss in bosses)
