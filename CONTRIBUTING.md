# Contributing

Use Python 3.13 and `uv`. Project versions come from `.python-version`,
`pyproject.toml`, and `uv.lock`.

## Local workflow

```bash
uv sync
make pre-commit-install
make check
```

Create a focused branch and keep each change small. Add or update a test when
behavior changes. Before opening a pull request, run:

```bash
make format
make check
make coverage
make web-check
```

## Code structure

- Put application transitions in `game/controller.py`.
- Keep Pygame event translation in `game/input_adapter.py`.
- Put drawing of application modes in `game/frame_renderer.py`.
- Pass time, input, random, and audio dependencies explicitly.
- Put shared test lifecycle in fixtures and reusable object construction in
  `tests/factories/`.
- Import from the defining module. Do not create proxy package exports.
- Write code comments and docstrings in English.
- Put player-facing text in `game/i18n.py` or use `LocalizedText`; provide both
  Ukrainian and English text.

Missing optional images may use the documented fallback and must log the full
resolved path. Required gameplay assets should fail with a precise error.

## Manual smoke check

For gameplay or rendering changes, verify this short path after automated checks:

1. Open the main menu and controls.
2. Select a location on the map and start the level.
3. Pause and resume with Escape, then open and close the map overlay.
4. Collect the required items and enter the boss fight.
5. Defeat the boss and continue to the next location.
6. Complete the final location and close the victory screen.

# Commit messages

Use Conventional Commits to keep generated GitHub release notes clear:

- `fix: restore boss collision` for a patch release;
- `feat: add language selector` for a minor release;
- include `BREAKING CHANGE:` in the body for a major release.
