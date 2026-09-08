# Releasing the game on itch.io

This guide updates the browser version at
[olharyzha.itch.io/marios-princess](https://olharyzha.itch.io/marios-princess).

## Before publishing

From the project root, install the locked dependencies and run all checks:

```bash
uv sync --locked
make check
make coverage
```

Run `make run` and verify the menu, both languages (`L`), movement, jumping,
pause, mute (`V`), boss selection, shooting with `J`, victory, progress saving,
and level unlocking.

## Build and test the web version

```bash
make web-build
```

The itch.io archive is created at `build/web.zip`. To test it locally, run:

```bash
make web-serve
```

Open `http://localhost:8000`. The command serves the same verified archive that
will be uploaded to itch.io.

If port 8000 is busy, use `make web-serve WEB_PORT=8001` and open
`http://localhost:8001`.

## Publish

Butler is already installed on this Mac. Authenticate once:

```bash
butler login
```

For every release after that, build and upload the game with one command:

```bash
make web-publish
```

This publishes `build/web.zip` to the `html5` channel of
`olharyzha/marios-princess`. Check the uploaded build with:

```bash
butler status olharyzha/marios-princess:html5
```

## Version and GitHub release

Release Please watches `development` and prepares a release PR from Conventional
Commits. Use `fix: ...` for patches, `feat: ...` for features, and add
`BREAKING CHANGE:` to the commit body for a major release. When that PR is
merged, GitHub automatically updates the project version, creates the matching
`vX.Y.Z` tag and GitHub Release, and attaches the verified browser build.

The release PR is the single place where the next version is reviewed. Do not
edit `pyproject.toml` or create version tags by hand.

## Troubleshooting

- **Old version is displayed:** wait for itch.io to process the build, then use
  `Cmd + Shift + R`.
- **Blank screen or missing asset:** check filename capitalization and relative
  paths.
- **No sound:** click inside the game first so the browser can enable audio.
- **Butler authentication fails:** run `butler login` again.

Official documentation:

- [itch.io HTML5 uploads](https://itch.io/docs/creators/html5)
- [Butler uploads](https://itch.io/docs/butler/pushing.html)
- [Pygbag](https://github.com/pygame-web/pygbag)
