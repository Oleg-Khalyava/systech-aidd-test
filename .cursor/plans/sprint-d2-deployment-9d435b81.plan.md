<!-- 9d435b81-8834-4408-bac0-8be643c795c9 961b34f1-787f-44ec-b473-118b1a63907f -->
# План Спринта D2 - Развертывание на сервер

## Обзор

Развернуть приложение на production сервере вручную по пошаговой инструкции с использованием готовых Docker образов из GitHub Container Registry.

## Файлы для создания/изменения

### 1. devops/doc/guides/manual-deploy.md

Создать подробную пошаговую инструкцию на русском языке:

- Подготовка локального окружения (проверка SSH ключа)
- Подключение к серверу (SSH с использованием ключа)
- Создание структуры директорий на сервере
- Копирование файлов (docker-compose.prod.yml, .env, prompts/)
- Pull Docker образов из ghcr.io
- Запуск сервисов
- Выполнение миграций БД (создание новой SQLite БД)
- Проверка работоспособности (логи, healthcheck, curl)

### 2. .env.production

Создать шаблон файла окружения:

- Все переменные с описанием
- TELEGRAM_BOT_TOKEN, OPENROUTER_API_KEY (использовать существующие)
- DATABASE_PATH=/app/data/bot.db
- NEXT_PUBLIC_API_URL=http://92.255.78.249:8006
- Примеры значений

### 3. docker-compose.prod.yml

Обновить конфигурацию:

- Изменить порты: API 8006:8000, Frontend 3006:3000
- Убедиться, что используются образы из ghcr.io/oleg-khalyava/systech-aidd-test-*
- Добавить volume для alembic и prompts при необходимости

### 4. devops/deploy-check.sh

Создать скрипт проверки готовности к деплою:

- Проверка наличия обязательных файлов (docker-compose.prod.yml, .env)
- Проверка переменных окружения в .env
- Проверка доступности SSH к серверу
- Проверка установки Docker на сервере
- Валидация портов (3006, 8006)

## Ключевые детали

**Сервер:**

- IP: 92.255.78.249
- User: systech
- Рабочая директория: /opt/systech/oleg_h
- Порты: Frontend 3006, API 8006

**Docker образы:**

- ghcr.io/oleg-khalyava/systech-aidd-test-bot:latest
- ghcr.io/oleg-khalyava/systech-aidd-test-api:latest
- ghcr.io/oleg-khalyava/systech-aidd-test-frontend:latest

**База данных:**

- SQLite новая пустая БД
- Запустить alembic миграции внутри контейнера bot или api

**Файлы для копирования:**

- docker-compose.prod.yml
- .env (создать из .env.production)
- prompts/nutritionist.txt
- prompts/text2sql.txt

## Шаги выполнения

1. Создать manual-deploy.md с детальными командами
2. Создать .env.production шаблон
3. Обновить docker-compose.prod.yml (порты)
4. Следовать инструкции manual-deploy.md для деплоя
5. Проверить работоспособность всех сервисов
6. Протестировать API и Frontend через браузер

### To-dos

- [ ] Создать devops/doc/guides/manual-deploy.md с пошаговой инструкцией развертывания
- [ ] Создать .env.production шаблон со всеми переменными и описанием
- [ ] Обновить docker-compose.prod.yml с портами 3006 (frontend) и 8006 (api)
- [ ] Выполнить развертывание на сервере следуя manual-deploy.md
- [ ] Проверить работоспособность: логи, healthcheck, доступность сервисов