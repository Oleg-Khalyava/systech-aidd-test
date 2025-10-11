# Техническое видение проекта: LLM-ассистент в виде Telegram-бота

## Технологии

### Основное
- **Python 3.11+** - основной язык
- **uv** - управление зависимостями и виртуальным окружением
- **aiogram 3.x** - работа с Telegram Bot API (polling)
- **openai** - клиент для работы с LLM через Openrouter
- **python-dotenv** - загрузка переменных окружения

### Инфраструктура
- **make** - автоматизация задач (запуск, форматирование)

### Разработка
- **pytest** - тестирование (с pytest-asyncio, pytest-cov, pytest-mock)
- **black** - форматирование кода (line-length = 100)
- **ruff** - линтер и code quality (замена flake8, isort, pyupgrade)
- **mypy** - статическая проверка типов (strict mode)

### Хранение данных
- **In-memory** - хранение данных в классах Python (словари, списки)

### Логирование
- **Текстовый файл** - простое логирование в файл

## Принцип разработки

### Основные принципы
- **KISS (Keep It Simple, Stupid)** - максимальная простота решения
- **ООП** - объектно-ориентированное программирование
- **1 класс = 1 файл** - строгое соблюдение для читаемости
- **Минимум зависимостей** - только необходимые библиотеки

### Подход к разработке
- **Итеративная разработка** - сначала работающий MVP, потом улучшения
- **Явное лучше неявного** - понятный и читаемый код
- **Без оверинжиниринга** - никаких избыточных абстракций и паттернов

## Структура проекта

```
systech-aidd-test/
├── src/
│   ├── __init__.py
│   ├── main.py              # Точка входа, запуск бота
│   ├── bot.py               # Класс бота (aiogram)
│   ├── config.py            # Класс конфигурации
│   ├── conversation.py      # Класс для управления диалогами (с LRU cache)
│   ├── user.py              # Класс для управления пользователями (с LRU cache)
│   ├── dependencies.py      # Dependency Injection контейнер
│   ├── protocols.py         # Protocol интерфейсы (IUserStorage, ILLMClient)
│   ├── metrics.py           # Система метрик и мониторинга
│   ├── logger.py            # Настройка логирования
│   ├── handlers/
│   │   ├── __init__.py
│   │   └── handlers.py      # Обработчики сообщений и команд
│   └── middlewares/         # Middleware для aiogram
│       ├── __init__.py
│       ├── rate_limit.py    # Rate limiting middleware
│       └── logging_middleware.py  # Логирование middleware
├── llm/
│   ├── __init__.py
│   └── client.py            # Класс для работы с LLM
├── tests/
│   ├── __init__.py
│   ├── test_config.py       # Тесты конфигурации
│   ├── test_user.py         # Тесты пользователей
│   ├── test_conversation.py # Тесты диалогов
│   ├── test_integration.py  # Интеграционные тесты
│   ├── test_rate_limit.py   # Тесты rate limiting
│   ├── test_dependencies.py # Тесты DI
│   └── test_metrics.py      # Тесты метрик
├── docs/                    # Документация
│   ├── vision.md            # Техническое видение (этот файл)
│   ├── tasklist.md          # Основной план разработки
│   ├── tasklist_tech_debt.md # План устранения технического долга
│   └── code_review_summary.md # Результаты code review
├── logs/                    # Папка для логов
├── .env.example             # Пример переменных окружения
├── .env                     # Переменные окружения (не в git)
├── .gitignore
├── pyproject.toml           # Конфигурация uv + настройки инструментов
├── Makefile                 # Команды для запуска и проверки качества
└── README.md
```

## Архитектура проекта

### Схема взаимодействия компонентов

```
┌─────────────────┐
│  Telegram User  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│   Bot (aiogram) + Middleware            │
│   - RateLimitMiddleware (rate limiting) │
│   - LoggingMiddleware (логирование)     │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│   Handlers + Dependencies (DI)          │
│   - BotDependencies контейнер           │
│   - Обработка команд и сообщений        │
└────────┬────────────────────────────────┘
         │
         ├──────────────────────┬─────────────────────┐
         ▼                      ▼                     ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│  UserStorage     │  │ ConversationStorage│  │   LLM Client     │
│  (LRU + TTL)     │  │  (LRU + TTL)      │  │  (OpenRouter)    │
└──────────────────┘  └──────────────────┘  └──────────────────┘
         │                      │                     │
         └──────────────────────┴─────────────────────┘
                                │
                                ▼
                        ┌──────────────────┐
                        │     Metrics      │
                        │  (мониторинг)    │
                        └──────────────────┘
```

### Описание компонентов

#### Основные компоненты
- **Bot** - инициализация aiogram, polling, маршрутизация
- **Handlers** - обработка команд (/start, /clear, /stats) и текстовых сообщений
- **Conversation** - хранение истории диалога с LRU cache и TTL
- **User** - хранение данных пользователя с LRU cache и TTL
- **LLM Client** - отправка запросов к LLM, получение ответов
- **Config** - загрузка и хранение конфигурации из .env

#### Новые компоненты (улучшения)
- **BotDependencies** - Dependency Injection контейнер для зависимостей
- **Protocols** - Protocol интерфейсы (IUserStorage, IConversationStorage, ILLMClient)
- **Middleware** - промежуточные обработчики для rate limiting и логирования
- **Metrics** - система сбора метрик (requests, errors, tokens, cost, users)

#### Middleware компоненты
- **RateLimitMiddleware** - защита от spam (rate limiting)
- **LoggingMiddleware** - логирование всех запросов с временем обработки

## Модель данных

### User (класс пользователя)
```python
class User:
    chat_id: int             # ID чата в Telegram
    username: str            # Username
    first_name: str          # Имя
    current_role: str        # Текущая роль (системный промпт)
```

### Conversation (класс диалога)
```python
class Conversation:
    chat_id: int             # ID чата
    messages: list           # История сообщений [{role, content}]
```

### Message (структура сообщения)
```python
{
    "role": "user|assistant|system",
    "content": "текст сообщения"
}
```

### Хранение данных
- **UserStorage** - `OrderedDict` с LRU cache `{chat_id: (User, timestamp)}`
  - Максимум 1000 пользователей (конфигурируемо)
  - TTL 24 часа (конфигурируемо)
  - Автоматическое удаление старых при превышении лимита
- **ConversationStorage** - `OrderedDict` с LRU cache `{chat_id: (Conversation, timestamp)}`
  - Максимум 1000 диалогов (конфигурируемо)
  - TTL 24 часа (конфигурируемо)
  - Автоматическое удаление старых при превышении лимита

## Работа с LLM

### Конфигурация
```python
OPENROUTER_API_KEY = "..."
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
MODEL = "gpt-oss-20b"  # или другая модель
```

### Процесс работы
1. Получение сообщения от пользователя
2. Формирование контекста из истории диалога
3. Добавление системного промпта (роль)
4. Отправка запроса к OpenRouter API через openai client
5. Получение ответа от LLM
6. Сохранение в историю диалога
7. Отправка ответа пользователю

### Формат запроса к LLM
```python
messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."},
    ...
]
```

### Управление контекстом
- Максимум последних **10 сообщений** в контексте
- При превышении - удаление самых старых сообщений

## Сценарии работы

### 1. Первый запуск бота
```
1. Пользователь отправляет /start
2. Создается User с данными из Telegram
3. Создается Conversation для пользователя
4. Устанавливается роль по умолчанию
5. Отправляется приветственное сообщение
```

### 2. Обычный диалог
```
1. Пользователь отправляет текстовое сообщение
2. Проверяется наличие ответа в контексте диалога
3. Если ответ найден в контексте - используется он
4. Если не найден - сообщение добавляется в историю
5. Формируется контекст (системный промпт + история)
6. Отправляется запрос к LLM
7. Получается ответ от LLM
8. Ответ добавляется в историю диалога
9. Ответ отправляется пользователю
```

### 3. Команды бота
- **/start** - инициализация пользователя, приветствие
- **/clear** - очистка истории диалога
- **/stats** - статистика бота (только для админа)

## Подход к конфигурированию

### Структура .env файла
```bash
# Telegram Bot
TELEGRAM_BOT_TOKEN=your_telegram_bot_token

# OpenRouter API
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=gpt-oss-20b

# Bot Settings
DEFAULT_SYSTEM_PROMPT=Ты полезный AI-ассистент
MAX_CONTEXT_MESSAGES=10

# Storage Settings (LRU cache)
MAX_STORAGE_SIZE=1000
STORAGE_TTL_HOURS=24

# Rate Limiting
RATE_LIMIT_SECONDS=2

# Admin (для команды /stats)
ADMIN_CHAT_ID=123456789

# Logging
LOG_FILE=logs/bot.log
LOG_LEVEL=INFO
```

### Загрузка конфигурации
- Использование **python-dotenv** для загрузки переменных
- Все настройки загружаются в класс **Config**
- Валидация обязательных параметров при старте

## Подход к логгированию

### Уровни логирования
- **DEBUG** - детальная отладочная информация
- **INFO** - общая информация о работе бота
- **WARNING** - предупреждения
- **ERROR** - ошибки

### Что логируется
- Запуск и остановка бота
- Получение сообщений от пользователей
- Запросы к LLM API
- Ошибки при работе с API
- Выполнение команд

### Формат логов
```
[2024-10-10 12:30:45] INFO - Bot started
[2024-10-10 12:31:10] INFO - User 12345 sent message: "Привет"
[2024-10-10 12:31:12] INFO - LLM request sent for user 12345
[2024-10-10 12:31:15] INFO - LLM response received
[2024-10-10 12:31:15] ERROR - Failed to send message: Connection timeout
```

### Настройка
- Логи сохраняются в файл `logs/bot.log`
- Ротация файлов при достижении размера 10MB
- Хранение последних 5 файлов логов

---

## Качество кода и тестирование

### Инструменты контроля качества

#### Black (автоформатирование)
```bash
make format
```
- Line length: 100 символов
- Target version: Python 3.11
- Автоматическое форматирование всего кода

#### Ruff (линтер)
```bash
make lint
```
- Проверка синтаксиса и стиля
- Импорты и неиспользуемые переменные
- Сложность кода и best practices
- Безопасность (bandit subset)

#### Mypy (проверка типов)
```bash
make type-check
```
- Strict mode для максимальной строгости
- Проверка всех type hints
- Выявление несовместимых типов

#### Pytest (тестирование)
```bash
make test       # Запуск всех тестов
make test-cov   # С отчетом о покрытии
```
- Unit тесты для всех компонентов
- Интеграционные тесты для critical path
- Минимальное покрытие: 80%

### Требования к качеству кода

#### Обязательные требования
- ✅ **Type hints** для всех функций и методов
- ✅ **Docstrings** для публичных классов и методов
- ✅ **Покрытие тестами** ≥80%
- ✅ **Линтер проходит** без ошибок (ruff)
- ✅ **Type checker проходит** без ошибок (mypy)
- ✅ **Форматирование** соответствует black

#### Best practices
- Protocol вместо ABC для интерфейсов
- Dependency Injection вместо глобальных переменных
- LRU cache + TTL для in-memory storage
- Безопасная обработка ошибок (без утечки информации)
- Валидация всех входных данных
- Rate limiting для защиты от abuse

### Процесс разработки

```bash
# 1. Разработка
# - Пишем код согласно conventions.mdc
# - Добавляем type hints и docstrings

# 2. Форматирование
make format

# 3. Проверка качества
make lint
make type-check

# 4. Тестирование
make test-cov

# 5. Все проверки одной командой
make check
```

### Метрики проекта

#### Code Quality Score
- Архитектура: 9/10 (цель после рефакторинга)
- Security: 9/10 (цель после рефакторинга)
- Тестирование: 9/10 (цель после расширения тестов)
- Code Style: 10/10 (цель после настройки инструментов)
- Production Ready: 8/10 (цель после улучшений)
- Мониторинг: 7/10 (цель после добавления метрик)

**Общая оценка:** 8.7/10 (production ready)

---

## Безопасность и Production Ready

### Security Best Practices

#### Обработка ошибок
```python
# ✅ Правильно - не показываем детали пользователю
try:
    response = await llm_client.send_message(context)
except Exception as e:
    logger.error("LLM API error", exc_info=True)
    await message.answer("Произошла ошибка. Попробуйте позже.")
```

#### Валидация входных данных
- Проверка длины сообщений (MAX_MESSAGE_LENGTH = 4000)
- Проверка на пустые сообщения
- Sanitization опасных символов если нужно

#### Rate Limiting
- Ограничение: 1 сообщение в 2 секунды на пользователя
- Защита от финансовых потерь (LLM API стоит денег)
- Дружелюбные сообщения для пользователя

### Production Readiness

#### Memory Management
- LRU cache для storage (max_size = 1000)
- TTL для автоматической очистки (24 часа)
- Нет утечек памяти в long-running процессах

#### Resilience
- Retry logic для Telegram API (3 попытки)
- Graceful shutdown при SIGTERM/SIGINT
- Обработка всех exception types

#### Monitoring
- Логирование всех критичных событий
- Метрики: requests, errors, tokens, cost, users
- Команда /stats для мониторинга

---

## Связанные документы

- **Соглашения разработки:** [.cursor/rules/conventions.mdc](../.cursor/rules/conventions.mdc)
- **Процесс разработки:** [.cursor/rules/workflow.mdc](../.cursor/rules/workflow.mdc)
- **План разработки:** [tasklist.md](./tasklist.md)
- **Технический долг:** [tasklist_tech_debt.md](./tasklist_tech_debt.md)
- **Code Review:** [code_review_summary.md](./code_review_summary.md)
