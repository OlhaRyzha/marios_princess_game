import pygame
from game.utils import WIDTH, HEIGHT, VICTORY_DIM_COLOR, FONT_SIZE
from game.utils.fonts import load_font
from game.utils.images import load_image, scale_to_height


class VictoryModal:
    def __init__(self, *, title: str, lines: list[str], on_continue):
        self.title = title
        self.lines = lines
        self.on_continue = on_continue
        self.active = True
        self.footer_text: str | None = None
        self.title_font = load_font(int(FONT_SIZE * 1.6))
        self.body_font = load_font(int(FONT_SIZE * 1.1))
        self.avatar: pygame.Surface | None = None
        self._load_avatar()

    def _load_avatar(self) -> None:
        path = "assets/mario/greeting.png"
        try:
            img = load_image(path)
            self.avatar = scale_to_height(img, int(FONT_SIZE * 3.4))
        except Exception:
            self.avatar = None

    @staticmethod
    def _wrap_lines(
        lines: list[str], max_chars: int = 54, *, max_lines: int = 6
    ) -> list[str]:
        wrapped: list[str] = []
        for ln in lines:
            text = ln.strip()
            if not text:
                wrapped.append("")
                continue
            words = text.split()
            buf = ""
            for w in words:
                candidate = f"{buf} {w}".strip()
                if len(candidate) > max_chars:
                    if buf:
                        wrapped.append(buf)
                    buf = w
                else:
                    buf = candidate
            if buf:
                wrapped.append(buf)
        if not wrapped:
            wrapped = [""]
        if len(wrapped) > max_lines:
            wrapped = wrapped[: max_lines - 1] + ["…"]
        return wrapped

    def handle_event(self, e: pygame.event.Event):
        if not self.active:
            return
        if e.type == pygame.KEYDOWN and e.key in (
            pygame.K_RETURN,
            pygame.K_SPACE,
            pygame.K_ESCAPE,
        ):
            self.active = False
            if self.on_continue:
                self.on_continue()

    def draw(self, surface: pygame.Surface):
        if not self.active:
            return
        dim = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        dim.fill(VICTORY_DIM_COLOR)
        surface.blit(dim, (0, 0))

        card_w = int(WIDTH * 0.46)
        card_h = int(HEIGHT * 0.52)
        card = pygame.Rect(
            (WIDTH - card_w) // 2, (HEIGHT - card_h) // 2, card_w, card_h
        )

        pygame.draw.rect(surface, (248, 240, 246), card, border_radius=20)
        pygame.draw.rect(surface, (210, 120, 150), card, width=4, border_radius=20)

        title = self.title_font.render(self.title, True, (180, 70, 110))
        title_x = card.centerx - title.get_width() // 2

        lines = self._wrap_lines(self.lines, max_chars=44)
        y = card.y + 18 + title.get_height() + 14
        x = card.x + 24
        for ln in lines[:6]:
            surf = self.body_font.render(ln, True, (60, 40, 65))
            surface.blit(surf, (x, y))
            y += surf.get_height() + 6
        surface.blit(title, (title_x, card.y + 18))

        if self.avatar is not None:
            avatar_rect = self.avatar.get_rect()
            avatar_rect.right = card.right - 18
            avatar_rect.bottom = card.bottom - 72
            surface.blit(self.avatar, avatar_rect)

        footer_text = getattr(self, "footer_text", None)
        hint_text = (
            footer_text
            if footer_text is not None
            else (
                "Enter — завершити гру"
                if self.on_continue is None
                else "Enter — продовжити"
            )
        )
        hint = self.body_font.render(hint_text, True, (120, 90, 120))
        hint_bottom_margin = 18
        hint_top_offset = 28
        hint_min_gap = 12
        hint_y = card.bottom - hint.get_height() - hint_bottom_margin - hint_top_offset
        hint_y = max(hint_y, y + hint_min_gap)
        surface.blit(
            hint,
            (
                card.centerx - hint.get_width() // 2,
                hint_y,
            ),
        )
