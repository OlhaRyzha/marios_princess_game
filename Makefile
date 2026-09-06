.PHONY: install upgrade run format format-check lint test check pre-commit-install pre-commit clean

install:
	uv sync

upgrade:
	uv sync --upgrade

run:
	uv run python main.py

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

check: format-check test

pre-commit-install:
	uv run pre-commit install
	uv run pre-commit install --hook-type pre-push

pre-commit:
	uv run pre-commit run --all-files

clean:
	rm -rf .pytest_cache .ruff_cache htmlcov
	rm -f .coverage
