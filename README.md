# 🤖 Systech AIDD Test - Telegram LLM Assistant Bot

![Build Status](https://github.com/Oleg-Khalyava/systech-aidd-test/actions/workflows/build.yml/badge.svg?branch=day-6-devops)

> Production-ready Telegram-бот с интеграцией LLM через OpenRouter API

Telegram-бот на Python, который работает как AI-ассистент с использованием различных LLM моделей через OpenRouter. Проект следует принципам **KISS** (Keep It Simple, Stupid) и **SOLID**, создан с фокусом на простоту, надежность, безопасность и качество кода.

**Статус:** ✅ Production Ready (v3.0 - Sprint S1) | **Тестов:** 105+ | **Качество:** 9/10

---

## ✨ Основные возможности

- 💬 **Контекстные диалоги** - бот помнит историю разговора (до 10 последних сообщений)
- 💾 **Персистентное хранение** - SQLite база данных, история сохраняется между перезапусками
- 🔍 **Полнотекстовый поиск** - FTS5 для быстрого поиска по истории сообщений
- 🧠 **Интеграция с LLM** - использование различных моделей через OpenRouter API
- 🔄 **Управление контекстом** - команда `/clear` для начала нового диалога
- 🔒 **Безопасность** - rate limiting, валидация входных данных, скрытие внутренних ошибок
- 🗑️ **Soft delete** - безопасное удаление данных с возможностью восстановления
- 🏗️ **Чистая архитектура** - Dependency Injection, Repository pattern, SOLID принципы
- 🔄 **Миграции БД** - Alembic для управления версиями схемы базы данных
- 🐳 **Docker Ready** - готовый multi-stage Dockerfile с автоматическим применением миграций
- 📊 **Система метрик** - отслеживание запросов, ошибок, токенов и стоимости
- 🔄 **Надежность** - retry logic для сетевых сбоев, graceful shutdown
- 📝 **Полное логирование** - все действия записываются в файл с автоматической ротацией
- ⚙️ **Гибкая настройка** - конфигурация через переменные окружения
- ✅ **Высокое покрытие тестами** - 105+ тестов, покрытие кода
- 🚀 **Production Ready** - готов к развертыванию в продакшене

---

## 🐳 Быстрый старт с Docker

Самый быстрый способ запустить все сервисы проекта локально:

### Предварительные требования

- [Docker](https://www.docker.com/get-started) (версия 20.10+)
- [Docker Compose](https://docs.docker.com/compose/install/) (версия 2.0+)

### Запуск за 3 шага

**1. Клонируйте репозиторий:**
```bash
git clone <repository-url>
cd systech-aidd-test
```

**2. Настройте переменные окружения:**
```bash
cp .env.example .env
# Отредактируйте .env и добавьте ваши токены
```

**3. Запустите все сервисы:**
```bash
make docker-up
```

Или напрямую через docker-compose:
```bash
docker-compose up -d
```

### Доступ к сервисам

После запуска все сервисы будут доступны по адресам:

- 🎨 **Frontend Dashboard:** http://localhost:3000
- 🌐 **Backend API:** http://localhost:8000/docs
- 🤖 **Telegram Bot:** отправьте `/start` вашему боту в Telegram

### Полезные команды

```bash
# Посмотреть логи всех сервисов
make docker-logs

# Проверить статус контейнеров
make docker-status

# Остановить все сервисы
make docker-down

# Перезапустить сервисы
make docker-restart

# Очистить контейнеры и volumes
make docker-clean
```

### Что происходит при запуске?

Docker автоматически:
- 🔨 Собирает образы для всех 3 сервисов (Bot, API, Frontend)
- 🗄️ Применяет миграции базы данных
- 📁 Создает volumes для SQLite БД и логов
- 🔄 Настраивает автоматический перезапуск при сбоях
- 🌐 Пробрасывает порты для API (8000) и Frontend (3000)

### Структура сервисов

```
┌─────────────────────────────────────┐
│   Frontend (Next.js)                │
│   http://localhost:3000             │
│   - Dashboard с метриками           │
│   - Визуализация статистики         │
└──────────────┬──────────────────────┘
               │ HTTP API
               ▼
┌─────────────────────────────────────┐
│   Backend API (FastAPI)             │
│   http://localhost:8000             │
│   - REST API эндпоинты              │
│   - Статистика и метрики            │
└──────────────┬──────────────────────┘
               │ SQLite
               ▼
┌─────────────────────────────────────┐
│   Telegram Bot (aiogram)            │
│   - Обработка сообщений             │
│   - Интеграция с LLM                │
└─────────────────────────────────────┘
               │
               ▼
      SQLite Database (./data/bot.db)
```

---

## 🚀 CI/CD и готовые Docker образы

### Автоматическая сборка

Проект использует **GitHub Actions** для автоматической сборки и публикации Docker образов при каждом изменении кода.

**Статус сборки:** ![Build Status](https://github.com/Oleg-Khalyava/systech-aidd-test/actions/workflows/build.yml/badge.svg?branch=day-6-devops)

### Использование готовых образов из GitHub Container Registry

Вместо локальной сборки можно использовать готовые образы из GitHub Container Registry:

```bash
# Pull образов из registry
docker pull ghcr.io/oleg-khalyava/systech-aidd-test-bot:latest
docker pull ghcr.io/oleg-khalyava/systech-aidd-test-api:latest
docker pull ghcr.io/oleg-khalyava/systech-aidd-test-frontend:latest

# Или через Makefile (pull всех образов)
make docker-prod-pull
```

### Быстрый запуск с готовыми образами

```bash
# 1. Настройте .env файл
cp .env.example .env
# Отредактируйте .env

# 2. Pull образов
make docker-prod-pull

# 3. Запуск сервисов
make docker-prod-up

# 4. Проверка статуса
docker ps

# 5. Просмотр логов
make docker-prod-logs
```

### Команды для работы с production образами

| Команда | Описание |
|---------|----------|
| `make docker-prod-pull` | Скачать образы из registry |
| `make docker-prod-up` | Запустить сервисы из registry |
| `make docker-prod-down` | Остановить production сервисы |
| `make docker-prod-restart` | Перезапустить production сервисы |
| `make docker-prod-logs` | Показать логи production сервисов |

### Использование конкретной версии

```bash
# Использовать образ с конкретным commit SHA
IMAGE_TAG=sha-abc1234 make docker-prod-up

# Или
export IMAGE_TAG=sha-abc1234
make docker-prod-up
```

### Переключение между режимами

```bash
# Local Build - сборка из исходников
make docker-up

# Production - готовые образы из registry
make docker-prod-up
```

**Подробнее:** см. [devops/README.md](devops/README.md) и [DevOps Roadmap](devops/doc/devops-roadmap.md)

---

## 🛠️ Технологический стек

| Компонент | Технология | Назначение |
|-----------|-----------|-----------|
| **Язык** | Python 3.11+ | Основной язык разработки |
| **Bot Framework** | aiogram 3.x | Работа с Telegram Bot API |
| **LLM Client** | openai | Взаимодействие с OpenRouter API |
| **Database** | SQLite + FTS5 | Персистентное хранение + полнотекстовый поиск |
| **DB Driver** | aiosqlite | Async драйвер для SQLite |
| **Migrations** | Alembic | Управление версиями схемы БД |
| **Package Manager** | uv | Управление зависимостями |
| **Container** | Docker + Docker Compose | Контейнеризация приложения |
| **CI/CD** | GitHub Actions | Автоматическая сборка и публикация образов |
| **Registry** | GitHub Container Registry (ghcr.io) | Хранение Docker образов |
| **Testing** | pytest + pytest-asyncio + pytest-cov | Автоматическое тестирование |
| **Linting** | ruff | Быстрый линтер (E, W, F, I, N, UP, B, C4, SIM) |
| **Type Checking** | mypy | Статическая проверка типов (strict mode) |
| **Code Style** | black | Форматирование кода |
| **Config** | python-dotenv | Загрузка переменных окружения |

### Архитектура

```
┌─────────────────┐
│  Telegram User  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│       Bot (aiogram)             │
│  ┌──────────────────────────┐   │
│  │   Middleware Layer       │   │
│  │  • Rate Limiting         │   │
│  │  • Dependency Injection  │   │
│  └──────────────────────────┘   │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│     Handlers + Validators       │
│  (обработка команд и валидация) │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│    BotDependencies (DI)         │
│  ┌─────────────────────────┐    │
│  │ • UserRepository        │    │
│  │ • MessageRepository     │    │
│  │ • LLM Client (retry)    │    │
│  │ • RoleManager           │    │
│  │ • Config                │    │
│  └─────────────────────────┘    │
└────────┬────────┬───────────────┘
         │        │
         ▼        ▼
┌─────────────────┐  ┌──────────────────┐
│   LLM Client    │  │  SQLite Database │
│                 │  │   • users        │
└─────────────────┘  │   • messages     │
         │           │   • messages_fts │
         │           └──────────────────┘
         ▼
   OpenRouter API
```

---

## 📦 Установка и запуск

### Шаг 1: Установка uv (если еще не установлен)

**Windows:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Linux/macOS:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Шаг 2: Клонирование репозитория

```bash
git clone <repository-url>
cd systech-aidd-test
```

### Шаг 3: Установка зависимостей

```bash
make install
```

Или вручную:
```bash
uv sync --all-extras
```

### Шаг 4: Настройка переменных окружения

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
SYSTEM_PROMPT_FILE=prompts/nutritionist.txt
MAX_CONTEXT_MESSAGES=10
WELCOME_MESSAGE=я AI-ассистент на базе LLM. Задавай любые вопросы, и я постараюсь помочь!

# Database Settings
DATABASE_PATH=data/bot.db

# Logging (опционально)
LOG_FILE=logs/bot.log
LOG_LEVEL=INFO
```

См. полный пример в файле [.env.example](.env.example)

### Шаг 5: Получение токенов

#### Telegram Bot Token:
1. Найдите [@BotFather](https://t.me/botfather) в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям для создания бота
4. Скопируйте полученный токен в `.env`

#### OpenRouter API Key:
1. Зарегистрируйтесь на [OpenRouter](https://openrouter.ai/)
2. Получите API ключ в личном кабинете
3. Добавьте его в `.env`

### Шаг 6: Применение миграций базы данных

```bash
uv run alembic upgrade head
```

Миграции создадут все необходимые таблицы в БД SQLite.

### Шаг 7: Запуск бота

```bash
make run
```

Или напрямую:
```bash
uv run python -m src.main
```

Бот запущен! Отправьте ему команду `/start` в Telegram.

### 🐳 Запуск через Docker

> 💡 **Рекомендуется:** Для быстрого старта используйте Docker! См. подробный раздел [🐳 Быстрый старт с Docker](#-быстрый-старт-с-docker) выше.

Краткая версия:

```bash
# Настройка и запуск
cp .env.example .env
# Отредактируйте .env
make docker-up

# Просмотр логов
make docker-logs

# Остановка
make docker-down
```

---

## 🎮 Команды бота

| Команда | Описание |
|---------|----------|
| `/start` | Инициализация бота и приветствие |
| `/clear` | Очистка истории диалога (начать заново) |
| `/role` | Показать текущую роль и специализацию бота |
| `/help` | Список доступных команд |
| *Любой текст* | Отправка сообщения AI-ассистенту с учетом контекста |

---

## 📸 Демонстрация работы

<!-- Добавьте сюда скриншот или GIF с работой бота -->

> 💡 **Совет:** Сделайте скриншот диалога с ботом или запишите короткое GIF, показывающее основные функции, и добавьте сюда.

**Пример использования:**
```
Пользователь: /start
Бот: 👋 Привет! Я AI-ассистент...

Пользователь: Расскажи про Python
Бот: Python - это высокоуровневый...

Пользователь: А какие у него преимущества?
Бот: (помнит контекст и отвечает про Python)

Пользователь: /clear
Бот: 🧹 История диалога очищена...
```

---

## 🧪 Разработка

### Команды разработки

```bash
# Запуск тестов
make test

# Запуск тестов с отчетом о покрытии
make test-cov

# Форматирование кода
make format

# Проверка качества кода (ruff)
make lint

# Проверка типов (mypy)
make type-check

# Все проверки (lint + type-check + test)
make check

# Очистка кеша и временных файлов
make clean

# Справка по командам
make help
```

### 🗄️ Работа с базой данных

```bash
# Применить миграции
uv run alembic upgrade head

# Откатить последнюю миграцию
uv run alembic downgrade -1

# Откатить все миграции
uv run alembic downgrade base

# Создать новую миграцию (после изменения схемы)
uv run alembic revision -m "описание изменений"

# Просмотр истории миграций
uv run alembic history

# Текущая версия БД
uv run alembic current
```

**Схема базы данных:**

- `users` - пользователи бота (с soft delete)
  - id, username, first_name
  - created_at, last_accessed, deleted_at

- `messages` - история сообщений (с soft delete)
  - id, user_id, role, content, length
  - created_at, deleted_at
  - INDEX (user_id, created_at)

- `messages_fts` - FTS5 виртуальная таблица для полнотекстового поиска
  - Автоматически синхронизируется через триггеры

### 🔍 Code Quality

Проект использует современные инструменты контроля качества кода:

| Инструмент | Назначение | Команда |
|-----------|------------|---------|
| **ruff** | Быстрый линтер (E, W, F, I, N, UP, B, C4, SIM) | `make lint` |
| **mypy** | Статическая проверка типов (strict mode) | `make type-check` |
| **black** | Форматирование кода | `make format` |
| **pytest** | Запуск тестов | `make test` |
| **pytest-cov** | Покрытие кода тестами (≥30%) | `make test-cov` |

**Перед коммитом всегда запускайте:**
```bash
make check
```
Эта команда выполнит все проверки: lint, type-check и test.

### Структура проекта

```
systech-aidd-test/
├── src/                    # Исходный код бота
│   ├── main.py            # Точка входа приложения
│   ├── bot.py             # Класс бота (aiogram)
│   ├── config.py          # Управление конфигурацией
│   ├── logger.py          # Настройка логирования
│   ├── protocols.py       # Protocol интерфейсы (DI)
│   ├── dependencies.py    # Контейнер зависимостей (DI)
│   ├── validators.py      # Валидация входных данных
│   ├── metrics.py         # Система метрик
│   ├── role_manager.py    # Управление ролями и промптами
│   ├── database/          # Слой доступа к данным
│   │   ├── __init__.py
│   │   └── repository.py  # DatabaseManager, UserRepository, MessageRepository
│   ├── handlers/          # Обработчики команд и сообщений
│   │   └── handlers.py
│   └── middlewares/       # Middlewares для aiogram
│       ├── __init__.py
│       ├── rate_limit.py           # Rate limiting
│       └── dependency_injection.py  # Dependency Injection
├── llm/                   # LLM клиент
│   └── client.py         # Класс для работы с OpenRouter API (retry logic)
├── alembic/               # Миграции базы данных
│   ├── versions/          # Файлы миграций
│   │   └── 001_initial_schema.py
│   ├── env.py             # Async миграции
│   └── script.py.mako     # Шаблон миграций
├── tests/                 # Тесты (pytest) - 105+ тестов
│   ├── test_config.py         # Тесты конфигурации (18 тестов)
│   ├── test_integration.py    # Интеграционные тесты (8 тестов)
│   ├── test_rate_limit.py     # Тесты rate limiting (7 тестов)
│   ├── test_dependencies.py   # Тесты DI (7 тестов)
│   ├── test_metrics.py        # Тесты метрик (16 тестов)
│   ├── test_validators.py     # Тесты валидации (7 тестов)
│   ├── test_role_manager.py   # Тесты менеджера ролей
│   └── test_repository.py     # Тесты репозиториев (16 тестов)
├── data/                  # База данных (создается автоматически)
│   ├── .gitkeep          # Для git
│   └── bot.db            # SQLite база данных
├── docs/                  # Документация проекта
│   ├── vision.md              # Техническое видение
│   ├── idea.md                # Концепция проекта
│   ├── roadmap.md             # Roadmap спринтов
│   ├── tasklists/             # Планы разработки
│   ├── code_review_summary.md # Результаты code review
│   └── architecture_overview.md # Обзор архитектуры
├── prompts/               # Файлы промптов для ролей
│   └── nutritionist.txt   # Промпт нутрициолога
├── logs/                  # Логи бота (создается автоматически)
│   └── bot.log           # Файл логов с ротацией (10MB, 5 файлов)
├── .env                   # Переменные окружения (не в git)
├── .env.example          # Пример конфигурации
├── alembic.ini           # Конфигурация Alembic
├── Dockerfile            # Multi-stage Docker образ
├── docker-compose.yml    # Docker Compose конфигурация
├── entrypoint.sh         # Entrypoint для Docker (миграции + запуск)
├── .dockerignore         # Игнорируемые файлы для Docker
├── pyproject.toml        # Конфигурация проекта и зависимости
├── uv.lock               # Lock-файл зависимостей
├── Makefile              # Команды для разработки
├── presentation.md       # Презентация выполненной работы
└── README.md             # Этот файл
```

### Принципы разработки

Проект следует строгим принципам разработки:

- ✅ **KISS** (Keep It Simple, Stupid) - максимальная простота решений
- ✅ **SOLID** - применение принципов объектно-ориентированного проектирования
  - **Dependency Inversion**: Protocol interfaces вместо конкретных классов
  - **Single Responsibility**: каждый класс отвечает за одну задачу
  - **Open/Closed**: расширяемость через middleware и DI
- ✅ **1 класс = 1 файл** - строгое правило для читаемости
- ✅ **Dependency Injection** - слабая связанность компонентов
- ✅ **Минимум зависимостей** - только необходимые библиотеки
- ✅ **Явное лучше неявного** - понятный и читаемый код
- ✅ **Type Safety** - строгая типизация (mypy strict mode)
- ✅ **Без оверинжиниринга** - никаких избыточных абстракций

Подробнее см. [docs/vision.md](docs/vision.md)

---

## 📊 Статус проекта

### Реализовано (v1.0)
- ✅ Базовая инфраструктура проекта
- ✅ Telegram бот с aiogram
- ✅ Интеграция с LLM через OpenRouter
- ✅ Контекстные диалоги с ограничением истории
- ✅ Команды /start и /clear
- ✅ Полное логирование с ротацией
- ✅ Валидация конфигурации
- ✅ Комплексное тестирование (89 тестов, 70.17% покрытия)

### Реализовано (v2.0 - Production Ready)
**Дата завершения:** 11.10.2025

#### 🔒 Security & Validation
- ✅ Rate limiting (1 сообщение в 2 секунды)
- ✅ Валидация входных данных (макс 4000 символов)
- ✅ Скрытие внутренних ошибок от пользователей
- ✅ Graceful error handling

#### 🏗️ Architecture Refactoring
- ✅ Dependency Injection (DI) архитектура
- ✅ Protocol-based interfaces (SOLID)
- ✅ Убраны все глобальные переменные
- ✅ Retry logic для Telegram API (3 попытки)

#### ⚡ Memory & Performance
- ✅ LRU cache для UserStorage (макс 1000 записей)
- ✅ LRU cache для ConversationStorage (макс 1000 записей)
- ✅ TTL механизм (автоочистка через 24 часа)
- ✅ Защита от утечек памяти

#### 🔧 Code Quality Tools
- ✅ Ruff линтер (исправлено 294 ошибки)
- ✅ Mypy типизация (исправлено 60 ошибок)
- ✅ Black форматирование
- ✅ Автоматизация проверок (`make check`)

#### 🧪 Testing & Monitoring
- ✅ Интеграционные тесты (8 тестов)
- ✅ Unit тесты для middlewares (14 тестов)
- ✅ Система метрик (BotMetrics)
- ✅ Покрытие кода 70.17% (+37.48%)

**Результаты:**
- 🎯 Production Ready: 4/10 → 8/10 (+100%)
- 📊 Тесты: 43 → 89 (+107%)
- 🛡️ Security: 5/10 → 9/10 (+80%)
- 🏗️ Architecture: 7/10 → 9/10 (+29%)

См. детали в [docs/tasklist_tech_debt.md](docs/tasklist_tech_debt.md) и [presentation.md](presentation.md)

### Реализовано (Sprint S1 - Database Persistence)
**Дата завершения:** 16.10.2025

#### 💾 Database Layer
- ✅ SQLite база данных с FTS5 для полнотекстового поиска
- ✅ Async драйвер aiosqlite для работы с БД
- ✅ Repository pattern для слоя данных (без ORM)
- ✅ Soft delete для users и messages
- ✅ Автоматическое вычисление метаданных (length, created_at)

#### 🔄 Migrations & Tooling
- ✅ Alembic для управления миграциями БД
- ✅ Async миграции с поддержкой aiosqlite
- ✅ Первая миграция: users, messages, messages_fts, триггеры
- ✅ Команды для upgrade/downgrade миграций

#### 🐳 Docker Infrastructure
- ✅ Multi-stage Dockerfile (builder + runtime)
- ✅ Docker Compose с volumes для data и logs
- ✅ Entrypoint скрипт с автоматическим применением миграций
- ✅ Готовый .dockerignore

#### 🧪 Testing
- ✅ 16 новых тестов для репозиториев (100% pass rate)
- ✅ Тесты DatabaseManager, UserRepository, MessageRepository
- ✅ Тесты FTS5 полнотекстового поиска
- ✅ Тесты soft delete механизма

**Результаты:**
- 💾 Данные теперь сохраняются между перезапусками
- 🔍 Готовый механизм полнотекстового поиска
- 🐳 Простой запуск через docker-compose
- 📊 Тесты: 89 → 105+ (+18%)

См. план спринта в [.cursor/plans/sprint-s1-database-bc5c0f7f.plan.md](.cursor/plans/sprint-s1-database-bc5c0f7f.plan.md)

### Планируется (будущие расширения)
- ⏳ Команда /role - переключение ролей AI
- ⏳ Команда /stats - статистика работы бота
- ⏳ Команда /search - полнотекстовый поиск по истории
- ⏳ Настройка параметров LLM (температура, max_tokens)
- ⏳ Экспорт истории диалога в файл
- ⏳ Поддержка голосовых сообщений
- ⏳ Потоковая передача ответов (streaming)
- ⏳ Поддержка изображений (vision models)

См. полный план в [docs/roadmap.md](docs/roadmap.md)

---

## 🔐 Безопасность и производительность

### Безопасность
- **Rate Limiting**: Защита от спама и DDoS атак (1 сообщение/2 сек)
- **Валидация входных данных**: Проверка длины и содержимого сообщений
- **Скрытие ошибок**: Внутренние детали не показываются пользователям
- **Soft delete**: Безопасное удаление с возможностью восстановления
- **Graceful shutdown**: Корректное закрытие БД и завершение работы

### Производительность
- **SQLite + WAL mode**: Быстрая БД с лучшей конкурентностью
- **FTS5 индексы**: Мгновенный полнотекстовый поиск по истории
- **Индексирование**: Оптимизированные индексы (user_id, created_at)
- **Async операции**: Неблокирующие запросы к БД через aiosqlite
- **Retry logic**: Автоматические повторные попытки при сетевых сбоях

### Персистентность
- **SQLite БД**: Все данные сохраняются между перезапусками
- **Миграции**: Версионирование схемы БД через Alembic
- **Docker volumes**: Персистентные тома для data/ и logs/
- **Транзакции**: ACID гарантии для целостности данных

### Мониторинг
- **Система метрик**: Отслеживание запросов, ошибок, токенов и стоимости
- **Детальное логирование**: Все важные события записываются в лог
- **Error tracking**: Полные traceback'и для отладки

---

## 📝 Лицензия

MIT License - свободное использование и модификация.

---

## 👨‍💻 Автор

**Systech AIDD Test Project**

Создано для демонстрации навыков разработки Telegram-ботов с интеграцией LLM.

---

## 🤝 Вклад в проект

Проект открыт для улучшений! Если вы хотите добавить новые функции или исправить ошибки:

1. Ознакомьтесь с [docs/vision.md](docs/vision.md) для понимания архитектуры
2. Изучите [docs/tasklist.md](docs/tasklist.md) для планирования
3. Следуйте принципам KISS и существующему стилю кода
4. Добавьте тесты для нового функционала

---

## 🔗 Полезные ссылки

- [Aiogram Documentation](https://docs.aiogram.dev/)
- [OpenRouter API](https://openrouter.ai/docs)
- [Python Telegram Bot Guide](https://core.telegram.org/bots/api)
- [UV Package Manager](https://github.com/astral-sh/uv)

---

**Вопросы?** Создайте issue в репозитории или обратитесь к документации в папке `docs/`.
