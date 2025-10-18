# 🚀 Быстрый старт с Docker

Запуск всех сервисов проекта за 3 минуты!

## Предварительные требования

- ✅ Docker (версия 20.10+)
- ✅ Docker Compose (версия 2.0+)
- ✅ Telegram Bot Token (от @BotFather)
- ✅ OpenRouter API Key (с https://openrouter.ai/)

## Шаг 1: Клонирование репозитория

```bash
git clone <repository-url>
cd systech-aidd-test
```

## Шаг 2: Настройка переменных окружения

```bash
# Создайте .env файл
cp .env.example .env

# Отредактируйте .env (минимум нужны эти 2 переменные):
# TELEGRAM_BOT_TOKEN=your_bot_token_here
# OPENROUTER_API_KEY=your_api_key_here
```

**Пример .env:**
```bash
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
OPENROUTER_API_KEY=sk-or-v1-abcdef1234567890
OPENROUTER_MODEL=gpt-oss-20b
DEFAULT_SYSTEM_PROMPT=Ты полезный AI-ассистент
```

## Шаг 3: Запуск всех сервисов

```bash
# Вариант 1: Через Make (рекомендуется)
make docker-up

# Вариант 2: Напрямую через docker-compose
docker-compose up -d
```

**Что происходит:**
- 🔨 Собираются 3 Docker образа (Bot, API, Frontend)
- 🗄️ Применяются миграции базы данных
- 🚀 Запускаются все контейнеры
- ⏱️ Займет 2-3 минуты при первом запуске

## Шаг 4: Проверка работоспособности

```bash
# Проверить статус контейнеров
make docker-status

# Ожидаемый вывод:
# NAME              STATUS          PORTS
# telegram-bot      Up 30 seconds
# backend-api       Up 30 seconds   0.0.0.0:8000->8000/tcp
# frontend-web      Up 30 seconds   0.0.0.0:3000->3000/tcp
```

## Шаг 5: Доступ к сервисам

### 🎨 Frontend Dashboard
Откройте в браузере: http://localhost:3000

### 🌐 Backend API
Откройте документацию API: http://localhost:8000/docs

Проверьте эндпоинт статистики:
```bash
curl http://localhost:8000/stats?period=week
```

### 🤖 Telegram Bot
1. Найдите вашего бота в Telegram
2. Отправьте команду `/start`
3. Начните диалог!

## 📊 Полезные команды

```bash
# Посмотреть логи всех сервисов
make docker-logs

# Посмотреть логи конкретного сервиса
docker-compose logs -f bot
docker-compose logs -f api
docker-compose logs -f frontend

# Проверить статус
make docker-status

# Перезапустить сервисы
make docker-restart

# Остановить все сервисы
make docker-down

# Очистить контейнеры и volumes
make docker-clean
```

## 🔧 Отладка

### Проблема: Контейнер не запускается

```bash
# Посмотреть логи
docker-compose logs <service-name>

# Примеры:
docker-compose logs bot
docker-compose logs api
docker-compose logs frontend
```

### Проблема: Порт уже занят

```bash
# Проверить, какой процесс использует порт
# Windows:
netstat -ano | findstr :3000
netstat -ano | findstr :8000

# Linux/Mac:
lsof -i :3000
lsof -i :8000

# Остановить docker-compose и освободить порты
make docker-down
```

### Проблема: База данных не создается

```bash
# Проверить, что миграции прошли успешно
docker-compose logs bot | grep "миграции"

# Проверить наличие БД
docker-compose exec bot ls -la data/

# Вручную применить миграции
docker-compose exec bot .venv/bin/alembic upgrade head
```

### Проблема: Frontend не подключается к API

```bash
# Проверить переменные окружения
docker-compose exec frontend env | grep API

# Должно быть:
# NEXT_PUBLIC_API_URL=http://localhost:8000

# Если нет, добавьте в .env:
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" >> .env
make docker-restart
```

## 🧪 Проверка всех компонентов

### 1. Проверка Bot
```bash
# Логи должны показывать успешный запуск
docker-compose logs bot | tail -20

# Должно быть:
# ✅ "Running database migrations..."
# ✅ "Starting bot..."
# ✅ "Bot started successfully"
```

### 2. Проверка API
```bash
# Тест эндпоинта здоровья
curl http://localhost:8000/health

# Тест статистики
curl http://localhost:8000/stats?period=week

# Открыть Swagger UI
open http://localhost:8000/docs  # Mac/Linux
start http://localhost:8000/docs  # Windows
```

### 3. Проверка Frontend
```bash
# Открыть в браузере
open http://localhost:3000  # Mac/Linux
start http://localhost:3000  # Windows

# Проверить логи Next.js
docker-compose logs frontend | tail -20

# Должно быть:
# ✅ "ready - started server on 0.0.0.0:3000"
# ✅ "compiled successfully"
```

### 4. Проверка интеграции

1. **Bot → Database:**
   ```bash
   # Отправьте сообщение боту в Telegram
   # Проверьте, что сообщение сохранилось в БД
   docker-compose exec bot ls -la data/bot.db
   ```

2. **API → Database:**
   ```bash
   # Проверьте, что API может читать данные
   curl http://localhost:8000/stats?period=week
   ```

3. **Frontend → API:**
   ```bash
   # Откройте http://localhost:3000
   # Dashboard должен показывать данные из API
   ```

## 📦 Архитектура

```
Frontend (3000) → API (8000) → Database
                              ↑
                           Bot
```

Все сервисы используют общую SQLite базу данных в `./data/bot.db`

## 🎉 Готово!

Теперь у вас работают все сервисы:
- ✅ Telegram Bot обрабатывает сообщения
- ✅ Backend API предоставляет статистику
- ✅ Frontend Dashboard показывает метрики

**Счастливой разработки! 🚀**

---

## 📚 Дополнительная документация

- [README.md](../README.md) - Основная документация
- [devops/README.md](README.md) - DevOps документация
- [devops/doc/sprint-d0-completed.md](doc/sprint-d0-completed.md) - Отчет о спринте

## 🆘 Нужна помощь?

Если что-то не работает:
1. Проверьте логи: `make docker-logs`
2. Проверьте статус: `make docker-status`
3. Посмотрите документацию: [devops/README.md](README.md)
4. Создайте issue в репозитории



