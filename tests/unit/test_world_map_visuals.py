from game.ui.world_map_visuals import lerp, mix_color, scale_color


def test_color_helpers_interpolate_and_clamp_channels() -> None:
    assert lerp(10.0, 20.0, 0.25) == 12.5
    assert mix_color((0, 10, 20), (100, 110, 120), 0.5) == (50, 60, 70)
    assert scale_color((200, 100, 10), 2.0) == (255, 200, 20)
