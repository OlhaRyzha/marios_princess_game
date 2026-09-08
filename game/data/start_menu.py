from game.actions import MenuAction, MenuItem

MAIN_MENU_ITEMS: tuple[MenuItem, ...] = (
    MenuItem("menu.start", MenuAction.START_GAME),
    MenuItem("menu.map", MenuAction.OPEN_MAP),
    MenuItem("menu.controls", MenuAction.OPEN_CONTROLS),
    MenuItem("menu.quit", MenuAction.QUIT),
)


def main_menu_items(*, is_web: bool) -> tuple[MenuItem, ...]:
    """Hide the unsupported browser quit action from the web menu."""
    return MAIN_MENU_ITEMS[:-1] if is_web else MAIN_MENU_ITEMS


PAUSE_MENU_ITEMS: tuple[MenuItem, ...] = (
    MenuItem("menu.resume", MenuAction.RESUME_GAME),
    MenuItem("menu.map", MenuAction.OPEN_MAP),
    MenuItem("menu.controls", MenuAction.OPEN_CONTROLS),
    MenuItem("menu.exit_to_menu", MenuAction.RETURN_TO_MENU),
)
