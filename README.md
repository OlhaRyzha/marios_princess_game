# 🎮 Mario’s Princess Game

A classic 2D **platformer** built with **Python and Pygame**.
Help the princess through colorful worlds, defeat bosses, and save Mario!

---

## 🌐 Play Online

You can play the game directly in your browser here:
👉 **[https://olharyzha.itch.io/marios-princess](https://olharyzha.itch.io/marios-princess)**

---

## 💻 Run locally

Follow the steps below to clone and run the game on your computer.

### 1. Clone the repository
```bash
git clone https://github.com/OlhaRyzha/marios_princess_game.git
cd marios_princess_game
```

### 2. Install uv

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) once on your computer.

### 3. Create the environment and install dependencies

```bash
uv sync
```

### 4. Run the game

```bash
make run
```

`uv sync` creates `.venv`, selects the Python version from `.python-version`, and installs the exact dependency versions from `uv.lock`. You do not need to activate the environment manually.

The game does not require a `.env` file. Headless SDL variables are set only by `make test`; machine-specific settings stay outside the source code.

## 🧰 Development

```bash
make format              # Fix Ruff issues and format with Black
make lint                # Check the code with Ruff
make test                # Run tests without opening a game window
make coverage            # Run tests and enforce the 60% branch coverage baseline
make check               # Run formatting, lint, and tests
make pre-commit-install  # Install Git hooks once
make pre-commit          # Check all tracked files manually
```

Runtime dependencies and development tools are declared separately in `pyproject.toml`. Do not edit `.venv` or `uv.lock` manually. Use `uv add <package>` for a game dependency and `uv add --dev <package>` for a development tool.

Tests are documented in [`tests/README.md`](tests/README.md). Shared resource lifecycle belongs in fixtures; reusable object construction belongs in factories.

## Project structure

```text
game/app.py              desktop/web runtime and frame sequence
game/controller.py       state transitions and progress commands
game/input_adapter.py    Pygame events routed to the active mode
game/frame_renderer.py   menu, map, game, and pause rendering
game/scene_factory.py    scene construction and dependency wiring
game/core/               gameplay actors and systems
game/data/               immutable game configuration
game/services/           adapters for external services such as audio
game/systems/            time, held input, and animation abstractions
game/utils/              paths, images, fonts, and constants
tests/unit/              focused behavior tests
tests/integration/       runtime flows across several components
tests/factories/         reusable deterministic test objects
```

The runtime explicitly passes time, held input, random generation, and audio to
the components that use them. Tests replace these dependencies with small fake
objects instead of patching Pygame globals.

## Configuration and assets

The game currently needs no `.env` file. Python and package versions are fixed
by `.python-version` and `uv.lock`. Asset paths are resolved from the repository
root, so `main.py` can be launched from another working directory. Optional
images render a visible fallback and log the full missing path; required
gameplay assets raise a precise `FileNotFoundError`.

## Adding a test

Choose `tests/unit/` for one component and `tests/integration/` for a complete
runtime transition. Use the headless `pygame_runtime` fixture when the test
creates surfaces. Add a factory only when multiple tests need configurable
instances. Run `make test` while working and `make coverage` before review.

## Web runtime

`game.app.run_game()` detects the Emscripten platform and uses an async frame
loop. Browser audio is armed after the first keyboard or mouse action. The
published browser version is linked above. Build the upload archive with:

```bash
make web-build
```

The archive is written to `build/web.zip`. The complete release and Butler
instructions are in
[`docs/itch-io-release.md`](docs/itch-io-release.md).

After the one-time `butler login`, build and publish a new version with
`make web-publish`.

Development rules and the review workflow are in
[`CONTRIBUTING.md`](CONTRIBUTING.md).

---

## 🕹️ Controls

| Action | Key |
|--------|-----|
| Move left / right | ← / → |
| Jump | Space |
| Attack | J |
| Crouch | ↓ |
| Start / Back | Enter / Esc |
