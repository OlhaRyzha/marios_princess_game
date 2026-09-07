import pygame

from game.services.audio import PygameAudioService


def test_audio_service_toggles_muted_state() -> None:
    audio = PygameAudioService()

    assert audio.toggle_muted()
    assert not audio.toggle_muted()


def test_runtime_input_toggles_audio(game_runtime) -> None:
    assert not game_runtime.audio_service.muted

    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_v))
    game_runtime.tick()

    assert game_runtime.audio_service.muted
