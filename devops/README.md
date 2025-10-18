# DevOps - Docker Setup

Эта папка содержит все необходимые файлы для запуска проекта через Docker.

## 📁 Структура

```
devops/
├── bot.Dockerfile          # Dockerfile для Telegram Bot
├── api.Dockerfile          # Dockerfile для Backend API
├── frontend.Dockerfile     # Dockerfile для Frontend
├── bot.dockerignore        # Игнорируемые файлы для Bot
├── api.dockerignore        # Игнорируемые файлы для API
├── frontend.dockerignore   # Игнорируемые файлы для Frontend
├── doc/
│   ├── devops-roadmap.md   # Roadmap DevOps спринтов
│   └── env-template.md     # Шаблон .env файла
└── README.md               # Этот файл
```

## 🚀 Быстрый старт

### 1. Настройка переменных окружения

Создайте файл `.env` в корне проекта:

```bash
# Скопируйте шаблон (из корня проекта)
cp .env.example .env

# Или создайте вручную, используя шаблон из devops/doc/env-template.md
```

Минимально необходимые переменные:
```bash
TELEGRAM_BOT_TOKEN=your_bot_token
OPENROUTER_API_KEY=your_api_key
```

### 2. Запуск всех сервисов

```bash
# Из корня проекта
make docker-up

# Или напрямую
docker-compose up -d
```

### 3. Проверка статуса

```bash
# Проверить статус контейнеров
make docker-status

# Посмотреть логи
make docker-logs
```

## 🐳 Docker команды

| Команда | Описание |
|---------|----------|
| `make docker-up` | Запустить все сервисы (detached mode) |
| `make docker-down` | Остановить все сервисы |
| `make docker-restart` | Перезапустить сервисы |
| `make docker-logs` | Показать логи (follow mode) |
| `make docker-status` | Показать статус контейнеров |
| `make docker-clean` | Очистить контейнеры и volumes |

## 📦 Сервисы

### Bot (Telegram Bot)
- **Dockerfile:** `devops/bot.Dockerfile`
- **Контейнер:** `telegram-bot`
- **Порты:** нет (работает через Telegram API)
- **Volumes:** `./data`, `./logs`

### API (Backend API)
- **Dockerfile:** `devops/api.Dockerfile`
- **Контейнер:** `backend-api`
- **Порты:** `8000:8000`
- **Volumes:** `./data`, `./logs`
- **URL:** http://localhost:8000/docs

### Frontend (Next.js)
- **Dockerfile:** `devops/frontend.Dockerfile`
- **Контейнер:** `frontend-web`
- **Порты:** `3000:3000`
- **URL:** http://localhost:3000

## 🔧 Архитектура

```
┌─────────────────────────────────────┐
│   Frontend (Next.js)                │
│   http://localhost:3000             │
│   Container: frontend-web           │
└──────────────┬──────────────────────┘
               │ HTTP API
               ▼
┌─────────────────────────────────────┐
│   Backend API (FastAPI)             │
│   http://localhost:8000             │
│   Container: backend-api            │
└──────────────┬──────────────────────┘
               │ SQLite
               ▼
┌─────────────────────────────────────┐
│   Telegram Bot (aiogram)            │
│   Container: telegram-bot           │
└──────────────┬──────────────────────┘
               │
               ▼
      SQLite Database (./data/bot.db)
```

## 🗂️ Volumes

- `./data:/app/data` - SQLite база данных (персистентная)
- `./logs:/app/logs` - Логи всех сервисов

## 🔍 Проверка работоспособности

### Bot
```bash
# Проверить логи
docker-compose logs bot

# Убедиться, что миграции применились
docker-compose exec bot ls -la data/

# Проверить, что БД создалась
docker-compose exec bot ls -la data/bot.db
```

### API
```bash
# Открыть документацию API
open http://localhost:8000/docs

# Проверить эндпоинт статистики
curl http://localhost:8000/stats?period=week
```

### Frontend
```bash
# Открыть в браузере
open http://localhost:3000

# Проверить логи
docker-compose logs frontend
```

## 🛠️ Отладка

### Просмотр логов конкретного сервиса
```bash
docker-compose logs -f bot
docker-compose logs -f api
docker-compose logs -f frontend
```

### Вход в контейнер
```bash
docker-compose exec bot /bin/bash
docker-compose exec api /bin/bash
docker-compose exec frontend /bin/sh
```

### Пересборка образов
```bash
# Пересобрать все образы
docker-compose build

# Пересобрать конкретный сервис
docker-compose build bot
docker-compose build api
docker-compose build frontend

# Пересобрать без кеша
docker-compose build --no-cache
```

### Очистка
```bash
# Остановить и удалить контейнеры
docker-compose down

# Остановить и удалить контейнеры + volumes
docker-compose down -v

# Удалить неиспользуемые образы
docker image prune -a
```

## 📋 Требования

- Docker версии 20.10 или выше
- Docker Compose версии 2.0 или выше
- 2GB свободного места на диске (для образов)
- Открытые порты: 3000 (Frontend), 8000 (API)

## 🔐 Безопасность

- ⚠️ Файл `.env` содержит секретные токены - **не коммитьте его в git**
- ✅ Используйте `.env.example` для шаблона
- ✅ В production используйте secrets management (Docker Secrets, Kubernetes Secrets)

## 📚 Дополнительная документация

- [DevOps Roadmap](doc/devops-roadmap.md) - план развития DevOps
- [Env Template](doc/env-template.md) - шаблон переменных окружения
- [Main README](../README.md) - основная документация проекта

## 🎯 Спринты

- ✅ **D0: Basic Docker Setup** (текущий) - базовая настройка Docker
- 📋 **D1: Build & Publish** - автоматическая сборка и публикация образов
- 📋 **D2: Server Deploy** - развертывание на сервере
- 📋 **D3: Auto Deploy** - автоматический деплой через GitHub Actions

См. полный план в [doc/devops-roadmap.md](doc/devops-roadmap.md)



