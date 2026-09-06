# План рефакторингу 2026

План побудований малими етапами. Кожен етап залишає гру робочою, має окрему перевірку й може бути переглянутий без великого diff.

## Критерії готовності всього рефакторингу

- новачок запускає проєкт трьома командами з README;
- версія Python і всі прямі залежності зафіксовані;
- runtime та dev-залежності розділені;
- один formatter (Black), один linter (Ruff), одна конфігурація тестів;
- тести працюють без реального дисплея та аудіопристрою;
- fixtures відповідають за lifecycle, factories — за побудову даних;
- основні переходи меню, мапи, гри й паузи перевірені;
- тестові сценарії детерміновані й не залежать від реального часу або глобального random;
- `run_frame` не містить усі правила застосунку;
- помилки ресурсів мають зрозумілу діагностику;
- README пояснює не лише команди, а й структуру проєкту та спосіб додати тест.

## Етап 0. Зафіксувати базову поведінку

Мета: відокремити вже наявні дефекти від помилок, внесених рефакторингом.

Зміни:

- додати короткий smoke-сценарій запуску головного меню в dummy video/audio mode;
- задокументувати підтримувані платформи: desktop і web;
- зафіксувати відомі дефекти паузи як regression-сценарії;
- зберегти список ручної перевірки: меню → мапа → рівень → boss → victory.

Готово, коли smoke-перевірка стабільно запускається локально й відомі дефекти мають відтворювані сценарії.

## Етап 1. Просте та відтворюване середовище

Мета: прибрати різницю між «у мене працює» та чистою машиною.

Зміни:

1. Додати `pyproject.toml` із:
   - підтримуваною версією Python;
   - `pygame` у runtime dependencies;
   - `pytest`, `pytest-cov` і `ruff` у групі `dev`;
   - `[tool.pytest.ini_options]`;
   - `[tool.ruff]`, lint і format правилами.
2. Додати `.python-version`.
3. Створити й закомітити `uv.lock`.
4. Прибрати ручний список транзитивних пакетів з `requirements.txt`; за потреби залишити його як згенерований експорт із чітким коментарем.
5. Перенести SDL setup з `.pylintrc` і `main.py` у маленьку функцію bootstrap, яка враховує платформу.
6. Додати `.env.example` тільки якщо з'явиться справжній runtime-параметр. Для поточного стану достатньо пояснити env variables у README без залежності `python-dotenv`.
7. Оновити README до команд:

   ```bash
   uv sync
   uv run python main.py
   uv run pytest
   ```

Рішення: Ruff замінює Flake8, pycodestyle, pyflakes і mccabe та впорядковує імпорти. Black залишається єдиним formatter. Відповідальності інструментів не перетинаються.

Готово, коли чисте середовище створюється однією командою, гра запускається, а lint/format/test використовують залежності з lock-файлу.

## Етап 2. Каркас тестів

Мета: створити маленьку, очевидну основу без надмірного мокінгу.

Зміни:

- `tests/conftest.py` встановлює `SDL_VIDEODRIVER=dummy`, `SDL_AUDIODRIVER=dummy`, ініціалізує Pygame і гарантовано викликає `pygame.quit()`;
- `tests/factories/` містить функції для побудови actor/state/runtime залежностей;
- `tests/unit/` не відкриває повну гру;
- `tests/integration/` перевіряє кілька компонентів разом;
- маркери використовуються лише за реальної потреби (`slow`, `integration`), а не для кожного тесту.

Перші тести:

1. `Animation` вибирає кадр, повторюється та зупиняється для `loop=False`.
2. `collide_mask` використовує маску та має rect fallback.
3. `boss_gate_position` не виходить за межі рівня.
4. Прогрес відкриває лише наступну локацію.
5. Переходи menu/map/game/pause повертають очікуваний режим.
6. Пауза не змінює позицію, health, timers і стан сцени.
7. Один headless кадр гри не падає.

Готово, коли тести читаються як короткі приклади використання коду, не залежать від порядку запуску та проходять повторно з однаковим результатом.

## Етап 3. Виправити дефекти паузи

Мета: виправити поведінку вже під захистом regression-тестів.

Зміни:

- розділити `scene.update()` і `scene.draw()`; на паузі викликати лише draw;
- не передавати `0.0` як сигнал паузи, бо частина фізики не масштабується через `dt`;
- визначити окремі menu items для головного меню та pause menu;
- додати доступний пункт `Продовжити гру`;
- перевірити Escape і кнопку продовження одним набором transition-тестів.

Готово, коли стан світу повністю заморожений на паузі, а обидва способи повернення до гри працюють.

## Етап 4. Чиста модель стану та прогресу

Мета: винести правила, які не потребують Pygame, у простий Python-код.

Зміни:

- замінити рядкові режими на `GameMode(StrEnum)`;
- замінити `GameState(TypedDict)` на `@dataclass`;
- створити невеликий `Progress` dataclass з методом `complete(location)`;
- винести transition-правила з `run_frame` у `GameController` або чисту функцію reducer;
- події UI перетворювати на типізовані команди (`START_GAME`, `OPEN_MAP`, `PAUSE`, `RESUME`, `QUIT`).

Цільовий потік:

```text
Pygame event → UI action → controller transition → state
                                               ↓
                                      active scene update/draw
```

Готово, коли прогрес і переходи тестуються без display, mixer, fonts та asset-файлів.

## Етап 5. Явні залежності для часу, input і random

Мета: отримати детерміновану логіку та показати dependency inversion без фреймворку.

Зміни:

- передавати поточний час або `Clock` protocol у системи cooldown;
- передавати `InputState` у player/scene замість читання `pygame.key.get_pressed()` усередині;
- передавати `random.Random` у obstacle/effects factories;
- мати production adapters для Pygame і прості fake-об'єкти в тестах;
- використовувати seeded RNG у тестах.

Готово, коли тести cooldown, руху та генерації перешкод не використовують monkeypatch глобальних функцій Pygame/random.

## Етап 6. Розділити великий ігровий цикл

Мета: застосувати SRP до координаторів без зміни gameplay.

Рекомендовані відповідальності:

```text
GameRuntime       — init/shutdown і desktop/web loop
GameController    — state transitions і progress
SceneManager      — створення та вибір активної сцени
InputAdapter      — Pygame events → game actions/input state
Renderer/scenes   — draw
AudioService      — mixer lifecycle і music commands
```

Порядок розділення:

1. Винести transition logic із `run_frame`.
2. Винести scene creation.
3. Винести audio arming та music policy.
4. Скоротити `run_frame` до послідовності input → transition → update → draw.
5. Розділити `DemoScene` на systems тільки там, де з'являється чітка незалежна відповідальність.

Готово, коли кожен компонент має коротке призначення, а зміна переходу меню не потребує редагування physics/render/audio коду.

## Етап 7. Ресурси, помилки та типи даних

Мета: прибрати залежність від current working directory й приховані збої.

Зміни:

- усі asset paths будувати від одного `ASSETS_DIR: Path`;
- описати assets через невеликий catalog/resolver;
- замінити broad exceptions на очікувані Pygame/OS exceptions;
- fallback-зображення залишити, але додати warning із точним шляхом;
- ввести dataclass для boss config та інших словників зі стабільним контрактом;
- використовувати `Path`, `Sequence`, `Mapping` і frozen dataclasses там, де дані незмінні.

Готово, коли гру можна запустити не з кореня репозиторію, а відсутній ресурс повідомляє, що саме не знайдено.

## Етап 8. Якість, документація та CI

Мета: зробити правила видимими й автоматичними.

Зміни:

- відформатувати код Ruff окремим mechanical commit;
- видалити `.flake8` і `.pylintrc` після перенесення потрібних правил;
- додати CI для `ruff check`, `ruff format --check`, `pytest`;
- встановити реалістичний початковий coverage threshold на критичну логіку, потім підвищувати його;
- доповнити README розділами «Структура», «Як запустити тести», «Як додати тест», «Конфігурація», «Web build»;
- додати короткий `CONTRIBUTING.md` з одним стандартним workflow.

Готово, коли pull request не може непомітно зламати форматування, lint або перевірені сценарії.

## Рекомендований порядок окремих гілок/PR

1. `chore/project-environment` — pyproject, uv, Python version, README.
2. `test/pygame-harness` — fixtures, factories, перші characterization tests.
3. `fix/pause-behavior` — замороження сцени й pause menu.
4. `refactor/game-state` — enum, dataclasses, progress, transitions.
5. `refactor/runtime-dependencies` — clock, input, RNG.
6. `refactor/game-loop` — controller/scene/audio boundaries.
7. `refactor/assets-errors` — paths, catalog, exception policy.
8. `chore/quality-ci-docs` — formatting, cleanup, CI, docs.

Кожна гілка повинна містити одну логічну зміну, відповідні тести та короткий опис «було → стало». Не слід змішувати масове форматування з архітектурною зміною: це ускладнює review і пошук регресій.

## Перша практична ітерація

Перший implementation slice має включати лише етапи 0–2:

- `pyproject.toml`, `.python-version`, `uv.lock`;
- Ruff для lint/imports і Black для форматування;
- оновлений README;
- headless Pygame fixture;
- невеликі actor/state factories;
- unit-тести animation/collision/progress;
- integration-тести переходів і паузи, причому відомі дефекти можна тимчасово позначити `xfail(strict=True)` до наступного етапу.

Це створить надійну основу. Після неї виправлення паузи й розділення станів стануть малими перевіреними змінами, а не переписуванням навмання.
