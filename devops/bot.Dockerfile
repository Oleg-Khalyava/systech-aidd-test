# Простой Dockerfile для Telegram Bot
FROM python:3.11-slim

WORKDIR /app

# Устанавливаем uv для быстрой установки зависимостей
RUN pip install uv

# Копируем файлы зависимостей
COPY pyproject.toml uv.lock ./

# Устанавливаем зависимости
RUN uv sync --no-dev

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

# Создаем директории для данных и логов
RUN mkdir -p /app/data /app/logs

# Запускаем через entrypoint (миграции + бот)
CMD ["./entrypoint.sh"]




