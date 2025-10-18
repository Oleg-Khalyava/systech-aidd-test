<!-- ea27712d-039c-4068-aa71-a935459bfe98 0a34eac3-937c-4437-8956-7d391b285af8 -->
# План Спринта D0: Basic Docker Setup

## Цель

Запустить все сервисы проекта (Bot, API, Frontend) локально через `docker-compose up` одной командой с фокусом на простоте и скорости.

## Основные задачи

### 1. Упростить Dockerfile для Bot

**Файл:** `Dockerfile`

Текущий Dockerfile использует multi-stage build, что избыточно для MVP. Нужно:

- Убрать multi-stage сборку
- Использовать один простой образ `python:3.11-slim`
- WORKDIR /app
- Установить зависимости через uv напрямую
- Копировать необходимые файлы (src/, llm/, prompts/, alembic/)
- Сохранить entrypoint.sh для миграций
- CMD через entrypoint.sh
- Размер: ~15-20 строк

### 2. Создать Dockerfile для API

**Файл:** `api/Dockerfile`

Создать простой Dockerfile для FastAPI сервиса:

- Базовый образ: `python:3.11-slim`
- WORKDIR /app
- Установка зависимостей через uv
- Копирование кода api/, llm/, prompts/
- Копирование alembic/ для миграций (API использует ту же БД)
- EXPOSE 8000
- CMD запуска: `uvicorn api.api_main:app --host 0.0.0.0 --port 8000`

### 3. Создать Dockerfile для Frontend

**Файл:** `frontend/Dockerfile`

Создать простой Dockerfile для Next.js приложения:

- Базовый образ: `node:20-alpine`
- Установка pnpm
- Установка зависимостей: `pnpm install`
- Команда запуска: `pnpm dev` (для локальной разработки)
- Порт: 3000

### 4. Обновить docker-compose.yml

**Файл:** `docker-compose.yml`

Добавить все три сервиса:

- **bot** (telegram-bot) - порт не нужен, работает через Telegram API
- **api** (backend-api) - порт 8000:8000
- **frontend** (frontend-web) - порт 3000:3000

Настройки для всех сервисов:

- Общий volume для SQLite БД: `./data:/app/data`
- Общий volume для логов: `./logs:/app/logs`
- env_file для переменных окружения
- restart: unless-stopped
- depends_on: API и Frontend зависят от Bot (БД инициализируется ботом)

### 5. Создать .dockerignore файлы для каждого сервиса

**Файлы:**

- `.dockerignore` (корень, для Bot)
- `api/.dockerignore` (для API)
- `frontend/.dockerignore` (для Frontend)

Для Bot (.dockerignore в корне):

- Расширить текущий файл
- Исключить: api/, frontend/, htmlcov/, devops/, docs/, tests/
- Оставить исключения для Python, git, IDE, logs

Для API (api/.dockerignore):

- Python кэш и виртуальное окружение
- frontend/, htmlcov/, devops/, docs/, tests/
- Git, IDE файлы, логи, .env
- Документация и markdown файлы

Для Frontend (frontend/.dockerignore):

- node_modules/, .next/, out/
- .git/, *.md, doc/
- IDE файлы (.vscode/, .idea/), логи, .env
- Python файлы и папки из корня

### 6. Добавить Make команды для Docker

**Файл:** `Makefile`

Добавить новый раздел "🐳 Docker commands":

- `make docker-up` - Запустить все сервисы (docker-compose up -d)
- `make docker-down` - Остановить все сервисы (docker-compose down)
- `make docker-restart` - Перезапустить сервисы
- `make docker-logs` - Показать логи всех сервисов (docker-compose logs -f)
- `make docker-status` - Показать статус контейнеров (docker-compose ps)
- `make docker-clean` - Очистить контейнеры и volumes

### 7. Обновить документацию

**Файл:** `README.md`

Добавить в начало файла раздел "🐳 Быстрый старт с Docker":

- Предварительные требования (Docker, Docker Compose)
- Настройка .env файла
- Одна команда для запуска: `make docker-up` или `docker-compose up`
- Полезные команды (логи, статус, остановка)
- URL для доступа к сервисам

### 8. Создать шаблон .env файла

**Файл:** `.env.example`

Создать пример с необходимыми переменными:

- BOT_TOKEN (Telegram bot token)
- OPENAI_API_KEY
- DATABASE_URL (sqlite:///data/bot.db)
- API_HOST, API_PORT
- FRONTEND_URL

### 9. Проверка работоспособности

После запуска `docker-compose up` выполнить проверку всех сервисов:

**Bot:**

- Проверить статус контейнера: `docker-compose ps`
- Проверить логи на наличие ошибок: `docker-compose logs bot`
- Убедиться, что миграции выполнились успешно
- Проверить, что БД создалась в `./data/bot.db`

**API:**

- Открыть в браузере http://localhost:8000/docs
- Проверить эндпоинт `/stats?period=week`
- Убедиться, что API отвечает 200 OK

**Frontend:**

- Открыть в браузере http://localhost:3000
- Проверить, что страница загружается
- Проверить подключение к API (dashboard должен отображать данные)

**Интеграция:**

- Проверить, что все три контейнера запущены
- Проверить, что логи пишутся в `./logs/`
- Проверить, что volume для БД работает корректно

## Критерии приемки

✅ Команда `docker-compose up` запускает все 3 сервиса
✅ Frontend доступен на http://localhost:3000
✅ API доступен на http://localhost:8000/docs
✅ Bot успешно подключается к Telegram
✅ Все сервисы используют общую SQLite БД
✅ Make команды работают корректно
✅ Документация обновлена и понятна

## Примечания

- Все Dockerfiles максимально простые (single-stage)
- Без оптимизаций кэширования (это будет в следующих спринтах)
- Фокус на работоспособности, а не на размере образов
- Используем dev режим для Next.js (не production build)

### To-dos

- [ ] Упростить Dockerfile для backend (убрать multi-stage build)
- [ ] Создать простой Dockerfile для API сервиса
- [ ] Создать простой Dockerfile для Frontend сервиса
- [ ] Обновить docker-compose.yml - добавить все 3 сервиса с правильными зависимостями
- [ ] Обновить .dockerignore для backend и создать для frontend
- [ ] Добавить Docker команды в Makefile (up, down, logs, status, clean)
- [ ] Обновить README.md с разделом быстрого старта через Docker
- [ ] Создать .env.example с шаблоном переменных окружения