from game.actions import MenuAction, MenuItem

MAIN_MENU_ITEMS: tuple[MenuItem, ...] = (
    MenuItem("menu.start", MenuAction.START_GAME),
    MenuItem("menu.map", MenuAction.OPEN_MAP),
    MenuItem("menu.controls", MenuAction.OPEN_CONTROLS),
    MenuItem("menu.quit", MenuAction.QUIT),
)

PAUSE_MENU_ITEMS: tuple[MenuItem, ...] = (
    MenuItem("menu.resume", MenuAction.RESUME_GAME),
    MenuItem("menu.map", MenuAction.OPEN_MAP),
    MenuItem("menu.controls", MenuAction.OPEN_CONTROLS),
    MenuItem("menu.quit", MenuAction.QUIT),
)
