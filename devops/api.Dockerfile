# Простой Dockerfile для FastAPI сервиса
FROM python:3.11-slim

WORKDIR /app

# Устанавливаем uv для быстрой установки зависимостей
RUN pip install uv

# Копируем файлы зависимостей
COPY pyproject.toml uv.lock ./

# Устанавливаем зависимости
RUN uv sync --no-dev

# Копируем код приложения
COPY api/ ./api/
COPY llm/ ./llm/
COPY prompts/ ./prompts/
COPY src/ ./src/

# Копируем файлы миграций (API использует ту же БД)
COPY alembic/ ./alembic/
COPY alembic.ini ./

# Создаем директории для данных и логов
RUN mkdir -p /app/data /app/logs

# Открываем порт для API
EXPOSE 8000

# Запускаем API сервер
CMD [".venv/bin/uvicorn", "api.api_main:app", "--host", "0.0.0.0", "--port", "8000"]



