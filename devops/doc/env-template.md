# Шаблон переменных окружения (.env)

Создайте файл `.env` в корне проекта и скопируйте содержимое ниже:

```bash
# ============================================
# Telegram Bot Configuration
# ============================================

# Telegram Bot Token (получите у @BotFather)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# ============================================
# OpenRouter API Configuration
# ============================================

# OpenRouter API Key (получите на https://openrouter.ai/)
OPENROUTER_API_KEY=your_openrouter_api_key_here

# OpenRouter API Base URL
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# Модель для использования (примеры: gpt-oss-20b, anthropic/claude-3-haiku, google/gemini-pro)
OPENROUTER_MODEL=gpt-oss-20b

# ============================================
# Bot Settings
# ============================================

# Системный промпт по умолчанию
DEFAULT_SYSTEM_PROMPT=Ты полезный AI-ассистент. Отвечай кратко и по существу.

# Файл с системным промптом (если нужна роль)
# SYSTEM_PROMPT_FILE=prompts/nutritionist.txt

# Максимальное количество сообщений в контексте
MAX_CONTEXT_MESSAGES=10

# Приветственное сообщение
WELCOME_MESSAGE=👋 Привет! Я AI-ассистент на базе LLM. Задавай любые вопросы, и я постараюсь помочь!

# ============================================
# Database Settings
# ============================================

# Путь к SQLite базе данных
DATABASE_PATH=data/bot.db

# ============================================
# API Settings (для Backend API)
# ============================================

# Хост API сервера
API_HOST=0.0.0.0

# Порт API сервера
API_PORT=8000

# ============================================
# Frontend Settings
# ============================================

# URL Backend API для Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000

# ============================================
# Logging Settings (опционально)
# ============================================

# Путь к файлу логов
LOG_FILE=logs/bot.log

# Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# ============================================
# Advanced Settings (опционально)
# ============================================

# Rate Limiting (секунды между сообщениями)
# RATE_LIMIT_SECONDS=2

# Максимальная длина сообщения от пользователя
# MAX_MESSAGE_LENGTH=4000

# Количество повторных попыток при сетевых ошибках
# MAX_RETRIES=3

# Задержка между повторными попытками (секунды)
# RETRY_DELAY=1
```

## Как использовать

1. Создайте файл `.env` в корне проекта:
   ```bash
   cp devops/doc/env-template.md .env
   ```

2. Отредактируйте `.env` и добавьте ваши реальные токены:
   - `TELEGRAM_BOT_TOKEN` - получите у @BotFather в Telegram
   - `OPENROUTER_API_KEY` - получите на https://openrouter.ai/

3. (Опционально) Настройте остальные параметры под ваши нужды

## Минимально необходимые переменные

Для запуска бота необходимы только эти две переменные:

```bash
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

Все остальные параметры имеют значения по умолчанию.



