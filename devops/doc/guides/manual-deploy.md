# Руководство по ручному развертыванию на production сервере

## Обзор

Данное руководство описывает процесс ручного развертывания приложения на production сервере с использованием Docker образов из GitHub Container Registry (ghcr.io).

**Параметры сервера:**
- IP адрес: `92.255.78.249`
- Пользователь: `systech`
- Рабочая директория: `/opt/systech/oleg_h`
- Порты: Frontend - `3006`, API - `8006`

**Docker образы:**
- `ghcr.io/oleg-khalyava/systech-aidd-test-bot:latest`
- `ghcr.io/oleg-khalyava/systech-aidd-test-api:latest`
- `ghcr.io/oleg-khalyava/systech-aidd-test-frontend:latest`

---

## Шаг 1: Подготовка локального окружения

### 1.1 Проверка наличия SSH ключа

Убедитесь, что у вас есть SSH ключ для подключения к серверу. Ключ должен быть предоставлен администратором.

**Проверка ключа:**
```bash
# Проверьте, что файл ключа существует (например, id_rsa_systech)
ls -la ~/.ssh/id_rsa_systech

# Установите правильные права доступа (обязательно!)
chmod 600 ~/.ssh/id_rsa_systech
```

### 1.2 Настройка SSH конфигурации (опционально)

Для удобства можно добавить настройки в `~/.ssh/config`:

```bash
# Откройте файл конфигурации
nano ~/.ssh/config

# Добавьте следующие строки:
Host systech-prod
    HostName 92.255.78.249
    User systech
    IdentityFile ~/.ssh/id_rsa_systech
    ServerAliveInterval 60
    ServerAliveCountMax 3
```

Теперь можно подключаться командой: `ssh systech-prod`

### 1.3 Запуск скрипта проверки (опционально)

Используйте автоматический скрипт проверки готовности:
```bash
# Запуск скрипта проверки
bash devops/deploy-check.sh

# Скрипт проверит:
# - Наличие всех необходимых файлов
# - Правильность конфигурации портов
# - SSH подключение к серверу
# - Docker на сервере
# - Доступность Docker образов
```

### 1.4 Проверка наличия необходимых файлов (вручную)

Если не запустили скрипт, проверьте вручную:
```bash
# В корне проекта
ls -la docker-compose.prod.yml
ls -la env.production.template
ls -la prompts/nutritionist.txt
ls -la prompts/text2sql.txt
```

### 1.5 Создание .env файла

Скопируйте шаблон и заполните переменные:
```bash
cp env.production.template .env
nano .env
```

**Обязательно заполните:**
- `TELEGRAM_BOT_TOKEN` - токен вашего Telegram бота
- `OPENROUTER_API_KEY` - API ключ OpenRouter
- `NEXT_PUBLIC_API_URL=http://92.255.78.249:8006` - URL API для frontend

---

## Шаг 2: Подключение к серверу

### 2.1 Проверка SSH подключения

```bash
# Если настроили SSH config:
ssh systech-prod

# Или напрямую с указанием ключа:
ssh -i ~/.ssh/id_rsa_systech systech@92.255.78.249
```

При первом подключении система запросит подтверждение fingerprint сервера - введите `yes`.

### 2.2 Проверка установленного ПО на сервере

После подключения к серверу проверьте наличие Docker и Docker Compose:

```bash
# Проверка Docker
docker --version
# Ожидаемый вывод: Docker version 24.x.x или выше

# Проверка Docker Compose
docker compose version
# Ожидаемый вывод: Docker Compose version v2.x.x или выше

# Проверка, что пользователь может использовать Docker
docker ps
# Если ошибка с правами доступа, обратитесь к администратору
```

---

## Шаг 3: Создание структуры директорий на сервере

Выполните команды на сервере (после SSH подключения):

```bash
# Переход в рабочую директорию
cd /opt/systech/oleg_h

# Создание структуры директорий
mkdir -p data logs prompts alembic/versions

# Проверка созданных директорий
ls -la
```

**Структура директорий:**
```
/opt/systech/oleg_h/
├── data/           # Для базы данных SQLite
├── logs/           # Для логов приложения
├── prompts/        # Для файлов промптов
├── alembic/        # Для миграций БД
│   └── versions/   # Для версий миграций
├── docker-compose.prod.yml
└── .env
```

---

## Шаг 4: Копирование файлов на сервер

Выполните команды на **локальной машине** (откройте новый терминал, не закрывая SSH сессию):

### 4.1 Копирование docker-compose.prod.yml

```bash
# Если настроили SSH config:
scp docker-compose.prod.yml systech-prod:/opt/systech/oleg_h/

# Или с указанием ключа:
scp -i ~/.ssh/id_rsa_systech docker-compose.prod.yml systech@92.255.78.249:/opt/systech/oleg_h/
```

### 4.2 Копирование .env файла

⚠️ **ВАЖНО:** Файл содержит секретные данные!

```bash
# Если настроили SSH config:
scp .env systech-prod:/opt/systech/oleg_h/

# Или с указанием ключа:
scp -i ~/.ssh/id_rsa_systech .env systech@92.255.78.249:/opt/systech/oleg_h/
```

### 4.3 Копирование файлов промптов

```bash
# Если настроили SSH config:
scp prompts/nutritionist.txt systech-prod:/opt/systech/oleg_h/prompts/
scp prompts/text2sql.txt systech-prod:/opt/systech/oleg_h/prompts/

# Или с указанием ключа:
scp -i ~/.ssh/id_rsa_systech prompts/nutritionist.txt systech@92.255.78.249:/opt/systech/oleg_h/prompts/
scp -i ~/.ssh/id_rsa_systech prompts/text2sql.txt systech@92.255.78.249:/opt/systech/oleg_h/prompts/
```

### 4.4 Копирование файлов миграций

```bash
# Копирование alembic.ini
scp -i ~/.ssh/id_rsa_systech alembic.ini systech@92.255.78.249:/opt/systech/oleg_h/

# Копирование файлов миграций
scp -i ~/.ssh/id_rsa_systech -r alembic/versions/ systech@92.255.78.249:/opt/systech/oleg_h/alembic/

# Копирование env.py для alembic
scp -i ~/.ssh/id_rsa_systech alembic/env.py systech@92.255.78.249:/opt/systech/oleg_h/alembic/
scp -i ~/.ssh/id_rsa_systech alembic/script.py.mako systech@92.255.78.249:/opt/systech/oleg_h/alembic/
```

### 4.5 Проверка скопированных файлов

Вернитесь в SSH терминал и проверьте:

```bash
cd /opt/systech/oleg_h

# Проверка основных файлов
ls -la docker-compose.prod.yml .env

# Проверка промптов
ls -la prompts/

# Проверка миграций
ls -la alembic/versions/

# Проверка содержимого .env (убедитесь, что токены заполнены)
cat .env | grep -E "TELEGRAM_BOT_TOKEN|OPENROUTER_API_KEY"
```

---

## Шаг 5: Загрузка Docker образов

Выполните команды на сервере (в SSH сессии):

### 5.1 Авторизация в GitHub Container Registry (если образы приватные)

Если ваши образы публичные, этот шаг можно пропустить.

```bash
# Создайте Personal Access Token в GitHub с правами read:packages
# Затем авторизуйтесь:
echo "YOUR_GITHUB_TOKEN" | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin
```

### 5.2 Загрузка образов

```bash
cd /opt/systech/oleg_h

# Загрузка всех образов через docker compose
docker compose -f docker-compose.prod.yml pull

# Проверка загруженных образов
docker images | grep systech-aidd-test
```

Ожидаемый вывод:
```
ghcr.io/oleg-khalyava/systech-aidd-test-bot        latest    ...
ghcr.io/oleg-khalyava/systech-aidd-test-api        latest    ...
ghcr.io/oleg-khalyava/systech-aidd-test-frontend   latest    ...
```

---

## Шаг 6: Запуск миграций базы данных

### 6.1 Проверка миграций

Сначала создадим временный контейнер для выполнения миграций:

```bash
cd /opt/systech/oleg_h

# Запускаем API контейнер в фоновом режиме для инициализации БД
docker compose -f docker-compose.prod.yml up -d bot

# Даем время на инициализацию (5-10 секунд)
sleep 10

# Проверяем, что контейнер запущен
docker compose -f docker-compose.prod.yml ps
```

### 6.2 Выполнение миграций

```bash
# Выполняем миграции через контейнер bot
docker compose -f docker-compose.prod.yml exec bot alembic upgrade head

# Проверка миграций
docker compose -f docker-compose.prod.yml exec bot alembic current
```

Ожидаемый вывод должен показать текущую версию миграции (например, `59aea0b85086`).

### 6.3 Проверка создания базы данных

```bash
# Проверка, что БД создана
ls -lh data/bot.db

# Проверка структуры БД (опционально)
docker compose -f docker-compose.prod.yml exec bot sqlite3 /app/data/bot.db ".tables"
```

Ожидаемый вывод: `alembic_version  messages  users`

---

## Шаг 7: Запуск всех сервисов

### 7.1 Запуск контейнеров

```bash
cd /opt/systech/oleg_h

# Остановка bot (если запущен с предыдущего шага)
docker compose -f docker-compose.prod.yml down

# Запуск всех сервисов в фоновом режиме
docker compose -f docker-compose.prod.yml up -d

# Проверка статуса контейнеров
docker compose -f docker-compose.prod.yml ps
```

Все контейнеры должны быть в состоянии `Up` или `running`.

### 7.2 Просмотр логов запуска

```bash
# Просмотр логов всех сервисов
docker compose -f docker-compose.prod.yml logs

# Просмотр логов конкретного сервиса
docker compose -f docker-compose.prod.yml logs bot
docker compose -f docker-compose.prod.yml logs api
docker compose -f docker-compose.prod.yml logs frontend

# Отслеживание логов в реальном времени
docker compose -f docker-compose.prod.yml logs -f
```

**Что искать в логах:**
- Bot: "Bot started. Press Ctrl+C to stop." или "Starting bot polling..."
- API: "Application startup complete" или "Uvicorn running on..."
- Frontend: "Ready in X ms" или "Local: http://localhost:3000"

---

## Шаг 8: Проверка работоспособности

### 8.1 Проверка статуса контейнеров

```bash
# Проверка запущенных контейнеров
docker compose -f docker-compose.prod.yml ps

# Проверка использования ресурсов
docker stats --no-stream
```

### 8.2 Проверка API через Health Check

```bash
# Проверка health endpoint API
curl http://localhost:8006/health

# Ожидаемый ответ:
# {"status":"ok"}

# Проверка root endpoint API
curl http://localhost:8006/

# Ожидаемый ответ должен содержать:
# {"message":"Telegram Bot Statistics API","documentation":"/docs","version":"1.0.0"}
```

### 8.3 Проверка API извне (с локальной машины)

Выполните на **локальной машине**:

```bash
# Проверка health endpoint
curl http://92.255.78.249:8006/health

# Проверка API documentation
curl http://92.255.78.249:8006/docs
```

### 8.4 Проверка Frontend

```bash
# На сервере
curl http://localhost:3006

# С локальной машины
curl http://92.255.78.249:3006
```

Откройте в браузере:
- **Frontend:** http://92.255.78.249:3006
- **API Docs:** http://92.255.78.249:8006/docs

### 8.5 Проверка Telegram бота

1. Откройте Telegram
2. Найдите вашего бота
3. Отправьте команду `/start`
4. Бот должен ответить приветственным сообщением

### 8.6 Проверка логов на наличие ошибок

```bash
# Проверка логов за последние 50 строк
docker compose -f docker-compose.prod.yml logs --tail=50

# Поиск ошибок в логах
docker compose -f docker-compose.prod.yml logs | grep -i error
docker compose -f docker-compose.prod.yml logs | grep -i warning
```

### 8.7 Проверка сетевого взаимодействия

```bash
# Проверка, что контейнеры могут общаться друг с другом
docker compose -f docker-compose.prod.yml exec frontend ping -c 3 api
docker compose -f docker-compose.prod.yml exec api ping -c 3 bot
```

---

## Шаг 9: Мониторинг и управление

### 9.1 Основные команды управления

```bash
cd /opt/systech/oleg_h

# Остановка всех сервисов
docker compose -f docker-compose.prod.yml stop

# Запуск остановленных сервисов
docker compose -f docker-compose.prod.yml start

# Перезапуск всех сервисов
docker compose -f docker-compose.prod.yml restart

# Перезапуск конкретного сервиса
docker compose -f docker-compose.prod.yml restart api

# Остановка и удаление контейнеров
docker compose -f docker-compose.prod.yml down

# Остановка и удаление контейнеров + volumes
docker compose -f docker-compose.prod.yml down -v
```

### 9.2 Обновление приложения

```bash
cd /opt/systech/oleg_h

# 1. Загрузка новых образов
docker compose -f docker-compose.prod.yml pull

# 2. Перезапуск с новыми образами
docker compose -f docker-compose.prod.yml up -d

# 3. Проверка логов
docker compose -f docker-compose.prod.yml logs -f
```

### 9.3 Просмотр логов

```bash
# Логи всех сервисов
docker compose -f docker-compose.prod.yml logs

# Логи за последние 100 строк
docker compose -f docker-compose.prod.yml logs --tail=100

# Логи с временными метками
docker compose -f docker-compose.prod.yml logs -t

# Логи в реальном времени
docker compose -f docker-compose.prod.yml logs -f

# Логи конкретного сервиса
docker compose -f docker-compose.prod.yml logs -f api
```

---

## Troubleshooting (Решение проблем)

### Проблема 1: Контейнер не запускается

**Симптомы:**
- Контейнер в статусе `Exited` или `Restarting`

**Диагностика:**
```bash
# Проверка статуса
docker compose -f docker-compose.prod.yml ps

# Просмотр логов проблемного контейнера
docker compose -f docker-compose.prod.yml logs [service_name]

# Проверка последних событий Docker
docker events --since 5m
```

**Возможные причины и решения:**

1. **Ошибка в .env файле:**
   ```bash
   # Проверьте все переменные
   cat .env
   
   # Особенно обязательные:
   grep TELEGRAM_BOT_TOKEN .env
   grep OPENROUTER_API_KEY .env
   ```

2. **Проблемы с правами доступа:**
   ```bash
   # Проверьте права на директории
   ls -la data/ logs/ prompts/
   
   # Исправьте права если нужно
   chmod 755 data logs prompts
   ```

3. **Порты уже заняты:**
   ```bash
   # Проверьте занятые порты
   sudo netstat -tlnp | grep -E "3006|8006"
   
   # Или с помощью ss
   sudo ss -tlnp | grep -E "3006|8006"
   
   # Остановите процесс или измените порты в docker-compose.prod.yml
   ```

### Проблема 2: API недоступен извне

**Симптомы:**
- API работает локально (curl http://localhost:8006/health)
- Но не доступен извне (curl http://92.255.78.249:8006/health)

**Диагностика:**
```bash
# Проверка firewall
sudo ufw status

# Проверка, что порты открыты
sudo netstat -tlnp | grep -E "3006|8006"
```

**Решения:**

1. **Открытие портов в firewall:**
   ```bash
   # Для Ubuntu/Debian
   sudo ufw allow 3006/tcp
   sudo ufw allow 8006/tcp
   sudo ufw reload
   
   # Для CentOS/RHEL
   sudo firewall-cmd --permanent --add-port=3006/tcp
   sudo firewall-cmd --permanent --add-port=8006/tcp
   sudo firewall-cmd --reload
   ```

2. **Проверка binding портов:**
   ```bash
   # API должен слушать на 0.0.0.0, а не только на 127.0.0.1
   docker compose -f docker-compose.prod.yml exec api netstat -tlnp
   ```

### Проблема 3: Frontend не может подключиться к API

**Симптомы:**
- Frontend загружается, но не показывает данные
- В браузере ошибки CORS или Network Error

**Диагностика:**
```bash
# Проверьте переменную NEXT_PUBLIC_API_URL в .env
grep NEXT_PUBLIC_API_URL .env

# Проверьте логи frontend
docker compose -f docker-compose.prod.yml logs frontend | grep -i error
```

**Решение:**
```bash
# Убедитесь, что NEXT_PUBLIC_API_URL правильный
# Должно быть: http://92.255.78.249:8006

# Если изменили .env, нужен rebuild frontend (т.к. это build-time переменная)
docker compose -f docker-compose.prod.yml up -d --build frontend
```

### Проблема 4: Telegram бот не отвечает

**Симптомы:**
- Бот не реагирует на команды в Telegram

**Диагностика:**
```bash
# Проверка логов бота
docker compose -f docker-compose.prod.yml logs bot | tail -100

# Проверка статуса контейнера
docker compose -f docker-compose.prod.yml ps bot
```

**Возможные причины:**

1. **Неверный TELEGRAM_BOT_TOKEN:**
   ```bash
   # Проверьте токен
   grep TELEGRAM_BOT_TOKEN .env
   
   # Если неверный, исправьте и перезапустите
   nano .env
   docker compose -f docker-compose.prod.yml restart bot
   ```

2. **Сетевые проблемы:**
   ```bash
   # Проверьте доступ к Telegram API
   docker compose -f docker-compose.prod.yml exec bot ping -c 3 api.telegram.org
   
   # Проверьте proxy настройки если используете
   ```

3. **Проблемы с webhook:**
   ```bash
   # Если ранее был настроен webhook, удалите его
   # Вставьте свой токен:
   curl https://api.telegram.org/bot<YOUR_TOKEN>/deleteWebhook
   
   # Затем перезапустите бота
   docker compose -f docker-compose.prod.yml restart bot
   ```

### Проблема 5: База данных не создается

**Симптомы:**
- Нет файла data/bot.db
- Ошибки при выполнении миграций

**Диагностика:**
```bash
# Проверьте наличие БД
ls -lh data/

# Проверьте права на директорию
ls -ld data/

# Проверьте логи
docker compose -f docker-compose.prod.yml logs bot | grep -i database
```

**Решение:**
```bash
# Убедитесь, что директория data существует и доступна для записи
mkdir -p data
chmod 755 data

# Выполните миграции вручную
docker compose -f docker-compose.prod.yml exec bot alembic upgrade head

# Если ошибка с alembic, проверьте файлы миграций
ls -la alembic/versions/
```

### Проблема 6: Высокое использование ресурсов

**Диагностика:**
```bash
# Проверка использования ресурсов
docker stats --no-stream

# Проверка места на диске
df -h

# Проверка размера логов
du -sh logs/
du -sh data/
```

**Решение:**
```bash
# Очистка старых логов
docker compose -f docker-compose.prod.yml logs --tail=0

# Очистка неиспользуемых Docker образов
docker image prune -a

# Очистка неиспользуемых volumes
docker volume prune

# Ограничение размера логов (уже настроено в docker-compose.prod.yml)
# max-size: "10m", max-file: "3"
```

### Проблема 7: После перезагрузки сервера контейнеры не запускаются

**Диагностика:**
```bash
# Проверка политики restart
docker compose -f docker-compose.prod.yml ps
```

**Решение:**
```bash
# Убедитесь, что в docker-compose.prod.yml есть:
# restart: unless-stopped

# Если нет, добавьте и перезапустите
docker compose -f docker-compose.prod.yml up -d
```

### Получение помощи

Если проблема не решена:

1. **Соберите диагностическую информацию:**
   ```bash
   # Сохраните вывод команд в файл
   docker compose -f docker-compose.prod.yml ps > debug.txt
   docker compose -f docker-compose.prod.yml logs >> debug.txt
   docker version >> debug.txt
   docker compose version >> debug.txt
   ```

2. **Проверьте документацию:**
   - [Docker Documentation](https://docs.docker.com/)
   - [Docker Compose Documentation](https://docs.docker.com/compose/)

3. **Обратитесь к администратору** с файлом debug.txt

---

## Полезные команды для ежедневной работы

```bash
# Быстрая проверка статуса
cd /opt/systech/oleg_h && docker compose -f docker-compose.prod.yml ps

# Просмотр логов за последний час
docker compose -f docker-compose.prod.yml logs --since 1h

# Перезапуск одного сервиса без остановки других
docker compose -f docker-compose.prod.yml restart api

# Обновление до новой версии
docker compose -f docker-compose.prod.yml pull && docker compose -f docker-compose.prod.yml up -d

# Backup базы данных
cp data/bot.db data/bot.db.backup.$(date +%Y%m%d_%H%M%S)

# Просмотр использования места
docker system df
```

---

## Чек-лист успешного развертывания

- [ ] SSH подключение работает
- [ ] Docker и Docker Compose установлены и работают
- [ ] Все файлы скопированы на сервер
- [ ] .env файл заполнен правильными значениями
- [ ] Docker образы успешно загружены
- [ ] Миграции БД выполнены успешно
- [ ] Все контейнеры запущены (status: Up)
- [ ] API health check возвращает {"status":"ok"}
- [ ] Frontend доступен в браузере
- [ ] Telegram бот отвечает на команды
- [ ] Нет ошибок в логах

---

## Следующие шаги

После успешного развертывания:

1. **Настройка мониторинга** (опционально)
2. **Настройка автоматических бэкапов БД**
3. **Настройка SSL сертификатов** (для HTTPS)
4. **Настройка CI/CD для автоматического деплоя** (Спринт D3)

---

**Дата создания:** 2025-10-18  
**Версия:** 1.0  
**Автор:** DevOps Team

