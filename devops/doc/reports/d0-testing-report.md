# Sprint D0 - Отчет о тестировании Docker Setup

**Дата тестирования:** 18 октября 2025
**Тестировщик:** Systech AIDD Team
**Версия:** 1.0

---

## 📋 Информация о системе

### Окружение
- **ОС:** Windows 10.0.19045
- **Docker:** 28.4.0, build d8eb465
- **Docker Compose:** v2.39.4-desktop.1
- **Рабочая директория:** F:\systech-aidd-test\systech-aidd-test

### Проверка предварительных условий

| Требование | Статус | Комментарий |
|------------|--------|-------------|
| Docker установлен | ✅ | Версия 28.4.0 |
| Docker Compose установлен | ✅ | Версия v2.39.4 |
| Docker Desktop запущен | ❌ | **Проблема #1** |
| Файл docker-compose.yml | ✅ | Найден |
| Файл devops/bot.Dockerfile | ✅ | Найден |
| Файл devops/api.Dockerfile | ✅ | Найден |
| Файл devops/frontend.Dockerfile | ✅ | Найден |
| Файл .env | ✅ | Найден |

---

## ❌ Найденные проблемы

### Проблема #1: Docker Desktop не запущен

**Описание:**
При попытке выполнения команды `docker-compose build` получена ошибка:

```
error during connect: Head "http://%2F%2F.%2Fpipe%2FdockerDesktopLinuxEngine/_ping": 
open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified.
```

**Причина:**
Docker Desktop не запущен или демон Docker недоступен.

**Решение:**
1. Запустить Docker Desktop из меню Пуск
2. Дождаться полной загрузки (иконка в трее должна стать зеленой)
3. Повторить команды тестирования

**Команда для проверки:**
```bash
docker ps
```

Если Docker работает, вы увидите список контейнеров (или пустой список, если контейнеров нет).

---

### Проблема #2: Ошибка WSL2 при запуске Docker Desktop (КРИТИЧЕСКАЯ)

**Описание:**
При попытке запуска Docker Desktop возникает ошибка:

```
Wsl/Service/RegisterDistro/CreateVm/ConfigureNetworking/HNS/0x80041002
c:\windows\system32\wsl.exe --import docker-desktop ... : exit status 0xffffffff
```

**Причина:**
Проблема с Host Networking Service (HNS) в Windows или конфликт сетевых настроек WSL2.

**Решения (попробуйте по порядку):**

#### Решение 1: Перезапуск службы HNS (БЫСТРОЕ)

Запустите PowerShell от имени администратора:

```powershell
# Остановить HNS
Stop-Service hns

# Запустить HNS
Start-Service hns

# Или рестарт одной командой
Restart-Service hns
```

После этого перезапустите Docker Desktop.

#### Решение 2: Очистка сетевых настроек Docker

Запустите PowerShell от имени администратора:

```powershell
# Остановить Docker Desktop полностью
Stop-Process -Name "Docker Desktop" -Force -ErrorAction SilentlyContinue

# Очистить виртуальные сети Docker
Get-HnsNetwork | Remove-HnsNetwork

# Перезапустить HNS
Restart-Service hns

# Запустить Docker Desktop снова
```

#### Решение 3: Полная очистка WSL и Docker

Запустите PowerShell от имени администратора:

```powershell
# 1. Остановить Docker Desktop
Stop-Process -Name "Docker Desktop" -Force -ErrorAction SilentlyContinue

# 2. Удалить docker-desktop и docker-desktop-data
wsl --unregister docker-desktop
wsl --unregister docker-desktop-data

# 3. Перезапустить HNS
Restart-Service hns

# 4. Перезапустить компьютер (рекомендуется)
Restart-Computer
```

После перезагрузки запустите Docker Desktop - он автоматически пересоздаст дистрибутивы WSL.

#### Решение 4: Сброс настроек Docker Desktop

1. Закрыть Docker Desktop полностью
2. Открыть Docker Desktop
3. Settings → Troubleshoot → Reset to factory defaults
4. Подтвердить сброс
5. Дождаться завершения
6. Перезапустить Docker Desktop

#### Решение 5: Переустановка WSL2 (если ничего не помогло)

Запустите PowerShell от имени администратора:

```powershell
# Обновить WSL
wsl --update

# Установить WSL2 как версию по умолчанию
wsl --set-default-version 2

# Перезагрузить компьютер
Restart-Computer
```

#### Решение 6: Временный обход (использовать Hyper-V вместо WSL2)

Если WSL2 продолжает давать сбои:

1. Открыть Docker Desktop
2. Settings → General
3. Снять галочку "Use the WSL 2 based engine"
4. Apply & Restart
5. Docker будет использовать Hyper-V (медленнее, но стабильнее)

**Рекомендуемый порядок действий:**

1. Попробовать Решение 1 (перезапуск HNS) - самое быстрое
2. Если не помогло - Решение 2 (очистка сетей)
3. Если не помогло - Решение 3 (полная очистка WSL)
4. Если не помогло - Решение 4 (сброс Docker)
5. Если проблема критична и нужно работать срочно - Решение 6 (Hyper-V)

**Статус:** ❌ КРИТИЧЕСКАЯ БЛОКИРУЮЩАЯ ПРОБЛЕМА

---

## 🧪 План тестирования

### 1. Валидация конфигурации

**Команда:**
```bash
docker-compose config
```

**Результат:** ✅ PASSED
- Синтаксис docker-compose.yml корректен
- Все 3 сервиса определены правильно:
  - `bot` (telegram-bot)
  - `api` (backend-api)
  - `frontend` (frontend-web)
- Зависимости настроены: frontend → api → bot
- Volumes настроены: ./data, ./logs
- Порты пробро шены: 8000 (API), 3000 (Frontend)

**Вывод конфигурации:**
```yaml
services:
  bot:
    build:
      context: F:\systech-aidd-test\systech-aidd-test
      dockerfile: devops/bot.Dockerfile
    container_name: telegram-bot
    restart: unless-stopped
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs

  api:
    build:
      context: F:\systech-aidd-test\systech-aidd-test
      dockerfile: devops/api.Dockerfile
    container_name: backend-api
    depends_on: [bot]
    ports: ["8000:8000"]
    restart: unless-stopped
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs

  frontend:
    build:
      context: F:\systech-aidd-test\systech-aidd-test
      dockerfile: devops/frontend.Dockerfile
    container_name: frontend-web
    depends_on: [api]
    ports: ["3000:3000"]
    restart: unless-stopped
```

### 2. Сборка образов

**Команды:**
```bash
# Сборка всех образов
docker-compose build

# Или по отдельности
docker-compose build bot
docker-compose build api
docker-compose build frontend
```

**Ожидаемый результат:**
- ✅ Bot образ собирается (~2-3 минуты, ~250MB)
- ✅ API образ собирается (~2-3 минуты, ~250MB)
- ✅ Frontend образ собирается (~3-4 минуты, ~450MB)

**Текущий статус:** ⏳ BLOCKED (требуется запуск Docker Desktop)

### 3. Запуск контейнеров

**Команда:**
```bash
docker-compose up -d
```

**Ожидаемый результат:**
```
Creating telegram-bot ... done
Creating backend-api  ... done
Creating frontend-web ... done
```

**Проверка статуса:**
```bash
docker-compose ps
```

**Ожидаемый вывод:**
```
NAME              STATUS          PORTS
telegram-bot      Up 30 seconds
backend-api       Up 30 seconds   0.0.0.0:8000->8000/tcp
frontend-web      Up 30 seconds   0.0.0.0:3000->3000/tcp
```

**Текущий статус:** ⏳ BLOCKED (требуется запуск Docker Desktop)

### 4. Проверка логов

**Команды:**
```bash
# Все логи
docker-compose logs

# Конкретный сервис
docker-compose logs bot
docker-compose logs api
docker-compose logs frontend

# Follow режим
docker-compose logs -f
```

**Ожидаемые логи для Bot:**
```
Running database migrations...
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
Starting bot...
Bot started successfully
```

**Ожидаемые логи для API:**
```
INFO:     Will watch for changes in these directories: ['/app']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Ожидаемые логи для Frontend:**
```
ready - started server on 0.0.0.0:3000, url: http://localhost:3000
info  - Loaded env from /app/.env
```

**Текущий статус:** ⏳ BLOCKED (требуется запуск Docker Desktop)

### 5. Тестирование сервисов

#### Bot (Telegram)

**Как проверить:**
1. Найти бота в Telegram (@your_bot_name)
2. Отправить команду `/start`
3. Отправить тестовое сообщение
4. Проверить ответ от LLM

**Ожидаемый результат:**
- ✅ Бот отвечает на `/start`
- ✅ Бот обрабатывает сообщения
- ✅ Сообщения сохраняются в БД

**Проверка БД:**
```bash
docker-compose exec bot ls -la data/
docker-compose exec bot ls -lh data/bot.db
```

**Текущий статус:** ⏳ BLOCKED

#### API (Backend)

**Как проверить:**

1. **Swagger UI:**
   - Открыть: http://localhost:8000/docs
   - Проверить наличие эндпоинтов
   - Выполнить тестовый запрос

2. **Health endpoint:**
   ```bash
   curl http://localhost:8000/health
   ```
   Ожидается: `200 OK`

3. **Stats endpoint:**
   ```bash
   curl http://localhost:8000/stats?period=week
   ```
   Ожидается: JSON с статистикой

**Текущий статус:** ⏳ BLOCKED

#### Frontend (Dashboard)

**Как проверить:**

1. **Главная страница:**
   - Открыть: http://localhost:3000
   - Проверить загрузку страницы
   - Проверить отображение компонентов

2. **Подключение к API:**
   - Dashboard должен загружать данные из API
   - Проверить отсутствие ошибок в консоли браузера (F12)

3. **Интерактивность:**
   - Проверить работу табов
   - Проверить отображение графиков
   - Проверить темную тему

**Текущий статус:** ⏳ BLOCKED

### 6. Проверка интеграции

**Сценарий:**
1. Отправить сообщение боту в Telegram
2. Проверить, что сообщение сохранилось в БД
3. Проверить, что API возвращает статистику
4. Проверить, что Frontend отображает данные

**Команды проверки:**
```bash
# Проверить БД
docker-compose exec bot ls -lh data/bot.db

# Проверить API
curl http://localhost:8000/stats?period=week

# Проверить логи
docker-compose logs bot | grep "message"
```

**Текущий статус:** ⏳ BLOCKED

### 7. Проверка volumes

**Команды:**
```bash
# Проверить data volume
ls -la ./data/

# Проверить logs volume
ls -la ./logs/

# Проверить размер БД
ls -lh ./data/bot.db
```

**Ожидаемый результат:**
- ✅ Директория ./data/ существует
- ✅ Файл bot.db создан
- ✅ Директория ./logs/ существует
- ✅ Файлы логов создаются

**Текущий статус:** ⏳ BLOCKED

### 8. Проверка Make команд

**Команды для тестирования:**

```bash
# Запуск
make docker-up

# Проверка статуса
make docker-status

# Просмотр логов
make docker-logs

# Перезапуск
make docker-restart

# Остановка
make docker-down

# Очистка
make docker-clean
```

**Ожидаемый результат:**
- ✅ Все команды работают без ошибок
- ✅ Help выводит корректную информацию

**Текущий статус:** ⏳ BLOCKED

---

## 📝 Инструкция по тестированию

### Шаг 1: Запуск Docker Desktop

1. Откройте Docker Desktop из меню Пуск
2. Дождитесь полной загрузки (иконка в трее станет зеленой)
3. Проверьте статус:
   ```bash
   docker ps
   ```

### Шаг 2: Сборка образов

```bash
# Вариант 1: Собрать все образы сразу
docker-compose build

# Вариант 2: Собрать по очереди с выводом прогресса
docker-compose build --progress=plain bot
docker-compose build --progress=plain api
docker-compose build --progress=plain frontend
```

**Ожидаемое время:** 8-10 минут при первой сборке

### Шаг 3: Запуск контейнеров

```bash
# Запуск в detached режиме
docker-compose up -d

# Или с выводом логов
docker-compose up
```

### Шаг 4: Проверка статуса

```bash
# Проверить статус контейнеров
docker-compose ps

# Проверить логи
docker-compose logs

# Проверить логи конкретного сервиса
docker-compose logs -f bot
```

### Шаг 5: Тестирование сервисов

#### Bot
```bash
# Проверить логи бота
docker-compose logs bot | Select-String "миграции"
docker-compose logs bot | Select-String "Starting bot"

# Отправить /start боту в Telegram
# Отправить тестовое сообщение
```

#### API
```bash
# Открыть в браузере
start http://localhost:8000/docs

# Или через curl
curl http://localhost:8000/health
curl http://localhost:8000/stats?period=week
```

#### Frontend
```bash
# Открыть в браузере
start http://localhost:3000

# Проверить логи
docker-compose logs frontend | Select-String "ready"
```

### Шаг 6: Проверка интеграции

1. Отправить сообщение боту
2. Проверить API: `curl http://localhost:8000/stats?period=week`
3. Открыть Frontend: `http://localhost:3000`
4. Убедиться, что данные отображаются

### Шаг 7: Остановка

```bash
# Остановить контейнеры
docker-compose down

# Или через Make
make docker-down
```

---

## 🐛 Потенциальные проблемы и решения

### Проблема: Порт уже занят

**Симптом:**
```
Error starting userland proxy: listen tcp4 0.0.0.0:3000: bind: address already in use
```

**Решение:**
```bash
# Найти процесс, использующий порт
netstat -ano | findstr :3000
netstat -ano | findstr :8000

# Остановить процесс
taskkill /F /PID <process_id>
```

### Проблема: Ошибка сборки образа

**Симптом:**
```
ERROR [internal] load metadata for docker.io/library/python:3.11-slim
```

**Решение:**
1. Проверить интернет-соединение
2. Перезапустить Docker Desktop
3. Попробовать пересобрать:
   ```bash
   docker-compose build --no-cache
   ```

### Проблема: Контейнер не запускается

**Решение:**
```bash
# Проверить логи
docker-compose logs <service_name>

# Проверить переменные окружения
docker-compose config

# Попробовать запустить в интерактивном режиме
docker-compose run <service_name> /bin/bash
```

### Проблема: База данных не создается

**Решение:**
```bash
# Проверить logs volume
ls ./data/

# Проверить права доступа
icacls ./data
icacls ./logs

# Вручную создать директории
mkdir -p ./data
mkdir -p ./logs

# Перезапустить контейнеры
docker-compose restart
```

### Проблема: Frontend не подключается к API

**Решение:**
1. Проверить переменные окружения:
   ```bash
   docker-compose exec frontend env | findstr API
   ```

2. Добавить в .env:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

3. Перезапустить:
   ```bash
   docker-compose restart frontend
   ```

---

## ✅ Checklist финального тестирования

После запуска Docker Desktop, выполните:

- [ ] `docker-compose build` - сборка без ошибок
- [ ] `docker-compose up -d` - запуск контейнеров
- [ ] `docker-compose ps` - все контейнеры "Up"
- [ ] `docker-compose logs bot` - миграции применились
- [ ] `ls ./data/bot.db` - БД создалась
- [ ] `curl http://localhost:8000/docs` - API доступен
- [ ] Открыть http://localhost:3000 - Frontend загружается
- [ ] Отправить `/start` боту - бот отвечает
- [ ] Отправить сообщение боту - бот отвечает
- [ ] Dashboard показывает данные - интеграция работает
- [ ] `docker-compose logs` - нет критических ошибок
- [ ] `make docker-down` - остановка без ошибок
- [ ] `make docker-up` - повторный запуск работает

---

## 📊 Итоговый статус

### Текущий статус: ❌ ТРЕБУЕТ УСТРАНЕНИЯ ПРОБЛЕМЫ WSL2

| Компонент | Статус | Комментарий |
|-----------|--------|-------------|
| Конфигурация docker-compose.yml | ✅ | Валидна |
| Dockerfile для Bot | ✅ | Создан |
| Dockerfile для API | ✅ | Создан |
| Dockerfile для Frontend | ✅ | Создан |
| .dockerignore файлы | ✅ | Созданы |
| Make команды | ✅ | Добавлены |
| Документация | ✅ | Обновлена |
| Docker Desktop | ❌ | **Проблема WSL2/HNS** |
| Сборка образов | ⏳ | Блокируется WSL2 |
| Запуск контейнеров | ⏳ | Блокируется WSL2 |
| Тестирование сервисов | ⏳ | Блокируется WSL2 |

### Критическая проблема:

**Проблема WSL2/HNS блокирует запуск Docker Desktop**

Ошибка: `Wsl/Service/RegisterDistro/CreateVm/ConfigureNetworking/HNS/0x80041002`

**Необходимые действия:**

1. **Попробовать быстрое решение** (Решение 1 выше):
   ```powershell
   # Запустить PowerShell от имени администратора
   Restart-Service hns
   ```
   Затем перезапустить Docker Desktop.

2. **Если не помогло** - следовать Решениям 2-6 по порядку (см. выше).

3. **Для срочной работы** - использовать Hyper-V вместо WSL2 (Решение 6).

### После устранения проблемы WSL2:

**Ожидаемый статус:** ✅ ВСЕ РАБОТАЕТ

Все файлы созданы правильно, конфигурация валидна. После устранения проблемы WSL2 и запуска Docker Desktop все должно работать без проблем.

---

## 📝 Рекомендации

### Немедленные действия:

1. **Запустить Docker Desktop** - основное блокирующее условие
2. **Выполнить полное тестирование** по инструкции выше
3. **Обновить этот отчет** с результатами реального тестирования

### Для следующего спринта (D1):

1. Добавить health checks в docker-compose.yml
2. Настроить автоматические тесты после сборки
3. Добавить CI/CD для автоматической проверки

### Улучшения:

1. Добавить `docker-compose.test.yml` для тестового окружения
2. Создать скрипт автоматического тестирования
3. Добавить мониторинг контейнеров

---

## 📚 Дополнительные материалы

- [devops/README.md](../README.md) - Основная документация
- [devops/QUICKSTART.md](../QUICKSTART.md) - Быстрый старт
- [devops/CHECKLIST.md](../CHECKLIST.md) - Полный checklist
- [docker-compose.yml](../../docker-compose.yml) - Конфигурация

---

**Подготовил:** Systech AIDD Team
**Дата:** 18 октября 2025
**Версия отчета:** 1.0
**Статус:** Предварительный (требуется запуск Docker Desktop для финального тестирования)

---

## 🔄 История изменений

| Дата | Версия | Изменения |
|------|--------|-----------|
| 18.10.2025 | 1.0 | Первоначальный отчет. Проверка конфигурации. Обнаружена проблема с Docker Desktop. |

---

**Следующий шаг:** Запустить Docker Desktop и выполнить полное тестирование по инструкции выше.

