# Mario's Princess Game

A 2D platform game built with Python and Pygame. Guide the princess through
three worlds, collect items, defeat each boss, and rescue Mario.

**[Play in your browser](https://olharyzha.itch.io/marios-princess)**

## Requirements

- Python 3.13
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- Make

The project does not use a `.env` file. Python is selected through
`.python-version`, and exact dependency versions are stored in `uv.lock`.

## Quick start

```bash
git clone https://github.com/OlhaRyzha/marios_princess_game.git
cd marios_princess_game
uv sync --locked
make run
```

`uv sync` creates and manages `.venv`, so manual environment activation is not
required.

## Controls

| Action | Key |
| --- | --- |
| Move | Left / Right arrows |
| Jump | Space |
| Attack | J |
| Crouch | Down arrow |
| Confirm | Enter |
| Pause / Back | Esc |
| Switch language | L |
| Mute / unmute | V |
| Toggle fullscreen | F11 |

## Development

| Command | Purpose |
| --- | --- |
| `make run` | Start the desktop game |
| `make format` | Apply Ruff fixes and Black formatting |
| `make lint` | Run Ruff checks |
| `make typecheck` | Run Pyright static type checks |
| `make docstrings-check` | Require English docstrings |
| `make test` | Run the test suite with headless SDL |
| `make coverage` | Run tests with the 70% branch coverage threshold |
| `make check` | Check formatting, types, docstrings, assets, and tests |
| `make web-check` | Build and validate the itch.io archive |
| `make pre-commit-install` | Install commit and push hooks |
| `make pre-commit` | Run every pre-commit hook |

Install the Git hooks once after cloning:

```bash
make pre-commit-install
```

Add runtime packages with `uv add <package>` and development tools with
`uv add --dev <package>`. Do not edit `.venv` or `uv.lock` manually.

## Project structure

```text
game/
├── app.py             # runtime and frame loop
├── controller.py      # state transitions and commands
├── input_adapter.py   # keyboard and window events
├── frame_renderer.py  # scene rendering
├── scene_factory.py   # scene construction
├── core/              # gameplay objects and combat
├── data/              # immutable game configuration
├── services/          # audio and external adapters
├── systems/           # time, input, and animation abstractions
├── ui/                # menus, map, HUD, and dialogs
└── utils/             # assets, paths, fonts, and constants
tests/
├── unit/              # isolated behavior tests
├── integration/       # multi-component runtime flows
└── factories/         # reusable deterministic test objects
```

Runtime dependencies such as time, held input, randomness, and audio are passed
explicitly to gameplay components. Tests use fixtures for shared lifecycle and
factories for reusable object construction. See [tests/README.md](tests/README.md)
for the testing conventions.

## Browser build and release

Build or run the Pygbag version locally:

```bash
make web-build  # creates build/web.zip
make web-serve  # serves the game locally
```

After the one-time `butler login`, publish a new itch.io version with:

```bash
make web-publish
```

See [docs/itch-io-release.md](docs/itch-io-release.md) for the complete release
checklist and troubleshooting steps.

Progress is saved automatically in browser storage or in
`~/.marios_princess_game/progress.json` for the desktop version.

The interface and story are available in Ukrainian and English. Press `L` at
any time to switch language; Ukrainian is the default.

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md) before making changes. It describes the
branch workflow, code quality rules, test layout, and review checklist.
