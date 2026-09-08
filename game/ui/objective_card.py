from collections.abc import Mapping

import pygame

from game.data.locations import LocationName
from game.data.objectives import ObjectiveConfig
from game.i18n import Localizer
from game.utils.constants import HEIGHT, WIDTH


def wrap_text(text: str, max_chars: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if current and len(candidate) > max_chars:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


class ObjectiveCard:
    def __init__(
        self,
        *,
        font: "pygame.font.Font",
        objectives: Mapping[LocationName, ObjectiveConfig],
        localizer: Localizer,
    ) -> None:
        self.font = font
        self.objectives = dict(objectives)
        self.localizer = localizer

    def draw(
        self,
        surface: "pygame.Surface",
        location: LocationName,
        *,
        locked: bool,
    ) -> None:
        objective = self.objectives.get(location)
        if objective is None:
            return

        description = " ".join(objective.lines(self.localizer))
        if locked:
            description = f'{self.localizer.text("map.locked")} {description}'
        wrapped = wrap_text(description, max_chars=74)[:4]
        if not wrapped:
            return

        padding_x = 24
        padding_y = 12
        line_gap = 4
        max_text_width = max(self.font.size(line)[0] for line in wrapped)
        card_width = min(int(WIDTH * 0.86), max_text_width + padding_x * 2)
        card_height = (
            padding_y * 2
            + len(wrapped) * self.font.get_height()
            + (len(wrapped) - 1) * line_gap
        )
        card = pygame.Rect(0, 0, card_width, card_height)
        card.centerx = WIDTH // 2
        card.bottom = HEIGHT - 20

        pygame.draw.rect(surface, (255, 240, 245), card, border_radius=16)
        pygame.draw.rect(surface, (255, 170, 190), card, 4, border_radius=16)

        color = (140, 120, 150) if locked else (150, 40, 70)
        y = card.y + padding_y
        for line in wrapped:
            text_surface = self.font.render(line, True, color)
            surface.blit(text_surface, (card.x + padding_x, y))
            y += self.font.get_height() + line_gap
