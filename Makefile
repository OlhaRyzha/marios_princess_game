.PHONY: install upgrade run web-build web-check web-serve web-publish format format-check lint typecheck docstrings-check assets-check version-check test coverage check pre-commit-install pre-commit clean

WEB_PORT ?= 8000

install:
	uv sync

upgrade:
	uv sync --upgrade

run:
	uv run python main.py

web-build:
	rm -rf build/web build/web.zip
	mkdir -p build/web
	uv run pygbag --build --archive --no_opt --template pygbag.tmpl --PYBUILD 3.13 .

web-check: web-build
	uv run python scripts/verify_web_build.py

web-serve: web-check
	uv run python -m http.server $(WEB_PORT) --directory build/web

web-publish: web-check
	butler push build/web.zip olharyzha/marios-princess:html5

format:
	uv run ruff check . --fix
	uv run black .

format-check:
	uv run ruff check .
	uv run black --check .

lint:
	uv run ruff check .

typecheck:
	uv run pyright
	uv run mypy game tests scripts main.py

docstrings-check:
	uv run python scripts/check_docstrings.py

assets-check:
	uv run python scripts/check_assets.py

version-check:
	uv run python scripts/check_version.py

test:
	SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy PYGAME_HIDE_SUPPORT_PROMPT=1 uv run pytest

coverage:
	SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy PYGAME_HIDE_SUPPORT_PROMPT=1 uv run pytest --cov=game --cov-report=term-missing:skip-covered

check: format-check typecheck docstrings-check assets-check version-check test

pre-commit-install:
	uv run pre-commit install
	uv run pre-commit install --hook-type pre-push

pre-commit:
	uv run pre-commit run --all-files

clean:
	rm -rf .pytest_cache .ruff_cache build htmlcov
	rm -f .coverage
