# Stage 1: Builder - устанавливаем зависимости
FROM python:3.11-slim as builder

WORKDIR /app

# Устанавливаем uv для быстрой установки зависимостей
RUN pip install uv

# Копируем файлы зависимостей
COPY pyproject.toml uv.lock ./

# Устанавливаем зависимости (без dev-зависимостей)
RUN uv sync --no-dev

# Stage 2: Runtime - минимальный образ для запуска
FROM python:3.11-slim

WORKDIR /app

# Копируем виртуальное окружение из builder
COPY --from=builder /app/.venv /app/.venv

# Копируем код приложения
COPY src/ ./src/
COPY llm/ ./llm/
COPY prompts/ ./prompts/

# Копируем файлы миграций
COPY alembic/ ./alembic/
COPY alembic.ini ./

# Копируем entrypoint скрипт
COPY entrypoint.sh ./
RUN chmod +x entrypoint.sh

# Создаем volumes для персистентных данных
VOLUME ["/app/data", "/app/logs"]

# Healthcheck для проверки работоспособности
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s \
    CMD python -c "import sys; sys.exit(0)"

# Запускаем через entrypoint (миграции + бот)
ENTRYPOINT ["./entrypoint.sh"]

