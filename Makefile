.PHONY: check lint format typecheck test privacy hooks

## Run every local check (CI runs the same set).
check: lint typecheck test privacy

lint:
	uv run ruff check .
	uv run ruff format --check .

format:
	uv run ruff format .
	uv run ruff check --fix .

typecheck:
	uv run mypy

test:
	uv run pytest

## Private files and values must never reach the repo.
privacy:
	uv run career-pilot privacy-check

## Opt-in: run `make check` before every push.
hooks:
	git config core.hooksPath .githooks
