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
make check               # Run formatting, lint, and tests
make pre-commit-install  # Install Git hooks once
make pre-commit          # Check all tracked files manually
```

Runtime dependencies and development tools are declared separately in `pyproject.toml`. Do not edit `.venv` or `uv.lock` manually. Use `uv add <package>` for a game dependency and `uv add --dev <package>` for a development tool.

Tests are documented in [`tests/README.md`](tests/README.md). Shared resource lifecycle belongs in fixtures; reusable object construction belongs in factories.

---

## 🕹️ Controls

| Action | Key |
|--------|-----|
| Move left / right | ← / → |
| Jump | Space |
| Attack | J |
| Crouch | ↓ |
| Start / Back | Enter / Esc |
