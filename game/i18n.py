from dataclasses import dataclass
from enum import StrEnum


class Language(StrEnum):
    UK = "uk"
    EN = "en"


@dataclass(frozen=True, slots=True)
class LocalizedText:
    uk: str
    en: str

    def get(self, language: Language) -> str:
        return self.uk if language is Language.UK else self.en


TRANSLATIONS: dict[Language, dict[str, str]] = {
    Language.UK: {
        "menu.start": "Почати гру",
        "menu.map": "Мапа світу",
        "menu.controls": "Керування",
        "menu.resume": "Продовжити гру",
        "menu.quit": "Вийти",
        "menu.exit_to_menu": "Вийти в головне меню",
        "menu.hint": "W/S: вибір  |  Enter: підтвердити  |  Esc: назад  |  L: English",
        "controls.title": "Керування",
        "controls.close": "Enter / Esc: закрити",
        "boss.about": "Опис:",
        "boss.strategy": "Стратегія:",
        "boss.goal": "Ціль:",
        "boss.hint": "A/D: змінити  •  Enter: обрати  •  Esc: закрити",
        "map.locked": "Пройди попередні локації, щоб відкрити цей рівень.",
        "victory.title": "Перемога!",
        "victory.boss": "Ти здолала боса!",
        "victory.next_goal": "Пройди наступний рівень і здолай боса, щоб врятувати Маріо.",
        "victory.next": "Далі: {location}",
        "victory.final_boss": "Ти здолала фінального боса!",
        "victory.mario_free": "Кришталева клітка розсипається — Маріо вільний.",
        "victory.celebrate": "Свято, конфеті й нові пригоди попереду!",
        "victory.finish": "Натисни Enter, щоб завершити гру",
        "victory.continue": "Enter: продовжити",
        "game.help": "A/D: рух  •  Space: стрибок  •  S: присісти  •  J: атака",
        "game.loading": "Завантаження…",
    },
    Language.EN: {
        "menu.start": "Start Game",
        "menu.map": "World Map",
        "menu.controls": "Controls",
        "menu.resume": "Resume Game",
        "menu.quit": "Quit",
        "menu.exit_to_menu": "Exit to main menu",
        "menu.hint": "W/S: select  |  Enter: confirm  |  Esc: back  |  L: Українська",
        "controls.title": "Controls",
        "controls.close": "Enter / Esc: close",
        "boss.about": "About:",
        "boss.strategy": "Strategy:",
        "boss.goal": "Goal:",
        "boss.hint": "A/D: change  •  Enter: select  •  Esc: close",
        "map.locked": "Complete the previous locations to unlock this level.",
        "victory.title": "You win!",
        "victory.boss": "You defeated the boss!",
        "victory.next_goal": "Clear the next level and defeat its boss to rescue Mario.",
        "victory.next": "Next: {location}",
        "victory.final_boss": "You defeated the final boss!",
        "victory.mario_free": "The crystal cage shatters and Mario is free.",
        "victory.celebrate": "Celebrate with confetti and prepare for new adventures!",
        "victory.finish": "Press Enter to finish the game",
        "victory.continue": "Enter: continue",
        "game.help": "A/D: move  •  Space: jump  •  S: crouch  •  J: attack",
        "game.loading": "Loading…",
    },
}


class Localizer:
    def __init__(self, language: Language = Language.UK) -> None:
        self.language = language

    def toggle(self) -> Language:
        self.language = Language.EN if self.language is Language.UK else Language.UK
        return self.language

    def text(self, key: str, **values: str) -> str:
        template = TRANSLATIONS[self.language].get(key, key)
        return template.format(**values)

    def resolve(self, value: LocalizedText) -> str:
        return value.get(self.language)
