# Systech AIDD Test - Telegram LLM Assistant Bot

Telegram-бот на Python с интеграцией LLM через OpenRouter API.

## 📋 Описание

Простой и понятный Telegram-бот, который работает как AI-ассистент с использованием LLM моделей через OpenRouter.

## 🚀 Технологии

- **Python 3.11+**
- **aiogram 3.x** - Telegram Bot API
- **openai** - клиент для OpenRouter API
- **uv** - управление зависимостями

## 📦 Установка

### 1. Установка uv (если еще не установлен)

```bash
# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Клонирование и настройка проекта

```bash
# Установка зависимостей
make install

# Или вручную
uv sync --all-extras
```

### 3. Настройка переменных окружения

Создайте файл `.env` в корне проекта:

```bash
# Telegram Bot
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# OpenRouter API
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=gpt-oss-20b

# Bot Settings
DEFAULT_SYSTEM_PROMPT=Ты полезный AI-ассистент
MAX_CONTEXT_MESSAGES=10
```

### 4. Получение токенов

**Telegram Bot Token:**
1. Найдите [@BotFather](https://t.me/botfather) в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям
4. Скопируйте полученный токен в `.env`

**OpenRouter API Key:**
1. Зарегистрируйтесь на [OpenRouter](https://openrouter.ai/)
2. Получите API ключ в личном кабинете
3. Добавьте его в `.env`

## 🎯 Запуск

```bash
make run
```

Или напрямую:

```bash
uv run python -m src.main
```

## 🧪 Тестирование

```bash
make test
```

## 🎨 Форматирование кода

```bash
make format
```

## 📁 Структура проекта

```
systech-aidd-test/
├── src/                    # Исходный код бота
│   ├── main.py            # Точка входа
│   ├── bot.py             # Класс бота
│   ├── config.py          # Конфигурация
│   ├── user.py            # Управление пользователями
│   ├── conversation.py    # Управление диалогами
│   └── handlers/          # Обработчики команд и сообщений
├── llm/                   # LLM клиент
│   └── client.py         # Класс для работы с OpenRouter API
├── tests/                 # Тесты
├── docs/                  # Документация
│   ├── vision.md         # Техническое видение
│   └── tasklist.md       # План разработки
├── logs/                  # Логи (создается автоматически)
├── pyproject.toml        # Конфигурация проекта
├── Makefile              # Команды для разработки
└── README.md             # Этот файл
```

## 📖 Команды бота

### Текущая версия (Итерация 2)
- `/start` - Инициализация и приветствие
- Любое текстовое сообщение - ответ от LLM с учетом контекста

### Планируется (следующие итерации)
- `/clear` - Очистка истории диалога
- `/role` - Переключение ролей
- Логирование событий

## 🔧 Разработка

Проект следует принципам:
- **KISS** - максимальная простота
- **ООП** - 1 класс = 1 файл
- **Минимум зависимостей**

Подробнее см. [docs/vision.md](docs/vision.md)

## 📝 Лицензия

MIT

## 👨‍💻 Автор

Systech AIDD Test Project
