from game.actions import MenuAction, MenuItem

MAIN_MENU_ITEMS: tuple[MenuItem, ...] = (
    MenuItem("Почати гру", MenuAction.START_GAME),
    MenuItem("Мапа світу", MenuAction.OPEN_MAP),
    MenuItem("Команди", MenuAction.OPEN_CONTROLS),
    MenuItem("Вийти", MenuAction.QUIT),
)

PAUSE_MENU_ITEMS: tuple[MenuItem, ...] = (
    MenuItem("Продовжити гру", MenuAction.RESUME_GAME),
    MenuItem("Мапа світу", MenuAction.OPEN_MAP),
    MenuItem("Команди", MenuAction.OPEN_CONTROLS),
    MenuItem("Вийти", MenuAction.QUIT),
)
