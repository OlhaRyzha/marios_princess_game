import pygame


def load_image(path: str, *, convert_alpha: bool = True) -> pygame.Surface:
    try:
        img = pygame.image.load(path)
        return img.convert_alpha() if convert_alpha else img.convert()
    except Exception:
        surf = pygame.Surface((64, 64), pygame.SRCALPHA)
        surf.fill((200, 100, 200, 255))
        pygame.draw.rect(surf, (30, 30, 30, 255), surf.get_rect(), 2)
        return surf


def scale_to_height(img: pygame.Surface, target_h: int) -> pygame.Surface:
    w, h = img.get_size()
    if h == 0:
        return img
    scale = target_h / h
    return pygame.transform.smoothscale(img, (int(w * scale), int(h * scale)))
