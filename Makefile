.PHONY: install upgrade run web-build web-serve web-publish format format-check lint test coverage check pre-commit-install pre-commit clean

install:
	uv sync

upgrade:
	uv sync --upgrade

run:
	uv run python main.py

web-build:
	rm -rf build/web build/web.zip
	mkdir -p build/web
	uv run pygbag --build --archive --no_opt --template pygbag.tmpl --PYBUILD 3.13 --disable-sound-format-error .

web-serve:
	uv run pygbag --template pygbag.tmpl --PYBUILD 3.13 --disable-sound-format-error .

web-publish: web-build
	butler push build/web.zip olharyzha/marios-princess:html5

format:
	uv run ruff check . --fix
	uv run black .

format-check:
	uv run ruff check .
	uv run black --check .

lint:
	uv run ruff check .

test:
	SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy PYGAME_HIDE_SUPPORT_PROMPT=1 uv run pytest

coverage:
	SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy PYGAME_HIDE_SUPPORT_PROMPT=1 uv run pytest --cov=game --cov-report=term-missing:skip-covered --cov-fail-under=60

check: format-check test

pre-commit-install:
	uv run pre-commit install
	uv run pre-commit install --hook-type pre-push

pre-commit:
	uv run pre-commit run --all-files

clean:
	rm -rf .pytest_cache .ruff_cache build htmlcov
	rm -f .coverage
