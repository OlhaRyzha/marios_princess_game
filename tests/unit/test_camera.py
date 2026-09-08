from game.presentation.camera import LevelCamera


def test_camera_follows_target_and_stays_inside_level() -> None:
    camera = LevelCamera(viewport_width=100, level_width=300)

    camera.follow(10)
    assert camera.x == 0

    camera.follow(180)
    assert camera.x == 130

    camera.follow(500)
    assert camera.x == 200

    camera.reset()
    assert camera.x == 0
