.PHONY: run format test install

install:
	uv sync --all-extras

run:
	uv run python -m src.main

format:
	uv run black src/ llm/ tests/

test:
	uv run pytest tests/ -v

