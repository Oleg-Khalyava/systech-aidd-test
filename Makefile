.PHONY: run stop format test install lint type-check check test-cov clean help api-run api-stop api-test api-docs fe-install fe-dev fe-stop fe-build fe-lint fe-format fe-type-check fe-check

install:
	uv sync --all-extras

run:
	uv run python -m src.main

api-run:
	uv run uvicorn api.api_main:app --reload --port 8000

api-stop:
	@powershell -Command "$$conn = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue; if ($$conn) { $$procId = $$conn.OwningProcess; taskkill /F /T /PID $$procId 2>$$null | Out-Null; Write-Host \"API server (PID $$procId) stopped\" } else { Write-Host 'No API server running on port 8000' }; exit 0"

api-test:
	@echo "Testing API endpoints..."
	@powershell -Command "try { $$response = Invoke-RestMethod -Uri 'http://localhost:8000/stats?period=week' -Method Get; $$response | ConvertTo-Json -Depth 10; Write-Host '✅ API test passed' } catch { Write-Host '❌ API test failed. Is the server running? (make api-run)'; exit 1 }"

api-docs:
	@echo "Opening API documentation..."
	@powershell -Command "Start-Process 'http://localhost:8000/docs'"

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

fe-install:
	cd frontend && pnpm install

fe-dev:
	cd frontend && pnpm dev

fe-stop:
	@powershell -Command "$$conn = Get-NetTCPConnection -LocalPort 3000 -State Listen -ErrorAction SilentlyContinue; if ($$conn) { $$procId = $$conn.OwningProcess; taskkill /F /T /PID $$procId 2>$$null | Out-Null; Write-Host \"Frontend dev server (PID $$procId) stopped\" } else { Write-Host 'No frontend dev server running on port 3000' }; exit 0"

fe-build:
	cd frontend && pnpm build

fe-lint:
	cd frontend && pnpm lint

fe-format:
	cd frontend && pnpm format

fe-type-check:
	cd frontend && pnpm type-check

fe-check: fe-lint fe-type-check
	@echo "✅ Frontend checks passed!"

help:
	@echo "═══════════════════════════════════════════════════════════════"
	@echo "  systech-aidd-test - Makefile Commands"
	@echo "═══════════════════════════════════════════════════════════════"
	@echo ""
	@echo "📦 Bot commands:"
	@echo "  make install     - Install all dependencies"
	@echo "  make run         - Run the Telegram bot"
	@echo "  make stop        - Stop all Python processes"
	@echo ""
	@echo "🌐 API commands (Backend):"
	@echo "  make api-run     - Run the statistics API server (port 8000)"
	@echo "  make api-stop    - Stop the API server"
	@echo "  make api-test    - Test API endpoints"
	@echo "  make api-docs    - Open API documentation in browser"
	@echo "                     URL: http://localhost:8000/docs"
	@echo ""
	@echo "🎨 Frontend commands:"
	@echo "  make fe-install   - Install frontend dependencies (pnpm)"
	@echo "  make fe-dev       - Run frontend dev server (port 3000)"
	@echo "                      URL: http://localhost:3000"
	@echo "  make fe-stop      - Stop the frontend dev server"
	@echo "  make fe-build     - Build frontend for production"
	@echo "  make fe-lint      - Run ESLint"
	@echo "  make fe-format    - Format frontend code with Prettier"
	@echo "  make fe-type-check - Run TypeScript type check"
	@echo "  make fe-check     - Run all frontend checks (lint + type-check)"
	@echo ""
	@echo "✅ Code quality (Backend):"
	@echo "  make format      - Format code with black"
	@echo "  make test        - Run tests"
	@echo "  make test-cov    - Run tests with coverage report"
	@echo "  make lint        - Run linter (ruff)"
	@echo "  make type-check  - Run type checker (mypy)"
	@echo "  make check       - Run all checks (lint + type-check + test)"
	@echo ""
	@echo "🛠️  Utility:"
	@echo "  make clean       - Clean cache and temp files"
	@echo "  make help        - Show this help message"
	@echo ""
	@echo "═══════════════════════════════════════════════════════════════"
	@echo "  Quick Start:"
	@echo "═══════════════════════════════════════════════════════════════"
	@echo ""
	@echo "  1. Install dependencies:"
	@echo "     make install && make fe-install"
	@echo ""
	@echo "  2. Run Backend API (in terminal 1):"
	@echo "     make api-run"
	@echo ""
	@echo "  3. Run Frontend (in terminal 2):"
	@echo "     make fe-dev"
	@echo ""
	@echo "  4. Open in browser:"
	@echo "     Frontend:  http://localhost:3000"
	@echo "     Backend:   http://localhost:8000/docs"
	@echo ""
	@echo "═══════════════════════════════════════════════════════════════"

