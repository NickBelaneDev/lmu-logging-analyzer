.PHONY: quality, fix

quality:
	uv sync --all-extras --dev
	uv run ruff check .
	uv run black --check .
	uv run mypy src

fix:
	uv run ruff check . --fix
	uv run black .
	uv run mypy src
