.PHONY: run stop format test install lint type-check check test-cov clean help

install:
	uv sync --all-extras

run:
	uv run python -m src.main

stop:
	@powershell -Command "$$procs = Get-Process python -ErrorAction SilentlyContinue; if ($$procs) { $$procs | Stop-Process -Force; Write-Host 'Bot stopped successfully' } else { Write-Host 'No Python processes running' }; exit 0"

format:
	uv run black src/ llm/ tests/

test:
	uv run pytest tests/ -v

test-cov:
	uv run pytest tests/ --cov=src --cov=llm --cov-report=html --cov-report=term-missing

lint:
	uv run ruff check src/ llm/ tests/

type-check:
	uv run mypy src/ llm/ tests/

check: lint type-check test
	@echo "✅ All checks passed!"

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .pytest_cache .coverage htmlcov .mypy_cache .ruff_cache 2>/dev/null || true

help:
	@echo "Available commands:"
	@echo "  make install     - Install all dependencies"
	@echo "  make run         - Run the bot"
	@echo "  make stop        - Stop all Python processes"
	@echo "  make format      - Format code with black"
	@echo "  make test        - Run tests"
	@echo "  make test-cov    - Run tests with coverage report"
	@echo "  make lint        - Run linter (ruff)"
	@echo "  make type-check  - Run type checker (mypy)"
	@echo "  make check       - Run all checks (lint + type-check + test)"
	@echo "  make clean       - Clean cache and temp files"
	@echo "  make help        - Show this help message"

