# ✅ Sprint D0 - Checklist проверки работоспособности

Используйте этот checklist для проверки корректности настройки Docker окружения.

## 📋 Предварительная проверка

- [ ] Docker установлен (версия 20.10+)
  ```bash
  docker --version
  ```

- [ ] Docker Compose установлен (версия 2.0+)
  ```bash
  docker-compose --version
  ```

- [ ] Порты 3000 и 8000 свободны
  ```bash
  # Windows:
  netstat -ano | findstr :3000
  netstat -ano | findstr :8000

  # Linux/Mac:
  lsof -i :3000
  lsof -i :8000
  ```

- [ ] Файл `.env` создан и содержит необходимые переменные
  ```bash
  cat .env | grep TELEGRAM_BOT_TOKEN
  cat .env | grep OPENROUTER_API_KEY
  ```

## 📦 Проверка структуры файлов

- [ ] Существует `devops/bot.Dockerfile`
- [ ] Существует `devops/api.Dockerfile`
- [ ] Существует `devops/frontend.Dockerfile`
- [ ] Существует `devops/bot.dockerignore`
- [ ] Существует `devops/api.dockerignore`
- [ ] Существует `devops/frontend.dockerignore`
- [ ] Файл `docker-compose.yml` содержит 3 сервиса (bot, api, frontend)

```bash
# Проверить все файлы одной командой:
ls -la devops/*.Dockerfile
ls -la devops/*.dockerignore
cat docker-compose.yml | grep "services:" -A 20
```

## 🚀 Проверка запуска

### 1. Сборка образов

- [ ] Сборка Bot образа
  ```bash
  docker-compose build bot
  # Должно завершиться без ошибок
  ```

- [ ] Сборка API образа
  ```bash
  docker-compose build api
  # Должно завершиться без ошибок
  ```

- [ ] Сборка Frontend образа
  ```bash
  docker-compose build frontend
  # Должно завершиться без ошибок
  ```

### 2. Запуск контейнеров

- [ ] Запуск всех сервисов
  ```bash
  make docker-up
  # или
  docker-compose up -d
  ```

- [ ] Проверка статуса контейнеров
  ```bash
  make docker-status
  # Все 3 контейнера должны быть в статусе "Up"
  ```

### 3. Проверка логов

- [ ] Логи Bot без ошибок
  ```bash
  docker-compose logs bot | tail -20
  # Должно содержать: "Running database migrations..." и "Starting bot..."
  ```

- [ ] Логи API без ошибок
  ```bash
  docker-compose logs api | tail -20
  # Должно содержать: "Uvicorn running on http://0.0.0.0:8000"
  ```

- [ ] Логи Frontend без ошибок
  ```bash
  docker-compose logs frontend | tail -20
  # Должно содержать: "ready - started server on 0.0.0.0:3000"
  ```

## 🔍 Проверка доступности сервисов

### Bot (Telegram)

- [ ] Бот отвечает в Telegram
  1. Найти бота в Telegram
  2. Отправить `/start`
  3. Получить приветственное сообщение
  4. Отправить тестовое сообщение
  5. Получить ответ от LLM

### API (Backend)

- [ ] API Docs доступны
  ```bash
  curl http://localhost:8000/docs
  # Должен вернуть HTML страницу с документацией
  ```

- [ ] Health endpoint работает
  ```bash
  curl http://localhost:8000/health
  # Должен вернуть 200 OK
  ```

- [ ] Stats endpoint работает
  ```bash
  curl http://localhost:8000/stats?period=week
  # Должен вернуть JSON с статистикой
  ```

- [ ] OpenAPI документация доступна в браузере
  - Открыть: http://localhost:8000/docs
  - [ ] Страница загружается
  - [ ] Видны эндпоинты API
  - [ ] Можно выполнить тестовый запрос

### Frontend (Dashboard)

- [ ] Frontend доступен в браузере
  - Открыть: http://localhost:3000
  - [ ] Страница загружается без ошибок
  - [ ] Отображается dashboard
  - [ ] Видны компоненты UI

- [ ] Frontend подключается к API
  - [ ] Данные с API отображаются на странице
  - [ ] Нет ошибок в консоли браузера (F12)

## 💾 Проверка базы данных

- [ ] База данных создана
  ```bash
  docker-compose exec bot ls -la data/
  # Должен быть файл bot.db
  ```

- [ ] База данных не пустая
  ```bash
  docker-compose exec bot ls -lh data/bot.db
  # Размер больше 0
  ```

- [ ] Миграции применены
  ```bash
  docker-compose logs bot | grep "миграции"
  # Должно быть: "Running database migrations..."
  ```

## 📁 Проверка volumes

- [ ] Volume для data существует
  ```bash
  ls -la ./data/
  # Должна быть директория с bot.db
  ```

- [ ] Volume для logs существует
  ```bash
  ls -la ./logs/
  # Должна быть директория с файлами логов
  ```

- [ ] Логи пишутся в файлы
  ```bash
  ls -la ./logs/
  # Должны быть log файлы
  cat ./logs/bot.log | tail -10
  ```

## 🔄 Проверка перезапуска

- [ ] Перезапуск сервисов работает
  ```bash
  make docker-restart
  docker-compose ps
  # Все контейнеры должны перезапуститься
  ```

- [ ] Остановка работает
  ```bash
  make docker-down
  docker-compose ps
  # Все контейнеры должны быть остановлены
  ```

- [ ] Повторный запуск работает
  ```bash
  make docker-up
  docker-compose ps
  # Все контейнеры должны запуститься снова
  ```

## 🧪 Проверка интеграции

- [ ] Bot → Database
  1. Отправить сообщение боту в Telegram
  2. Проверить логи: `docker-compose logs bot`
  3. Сообщение должно сохраниться в БД

- [ ] API → Database
  ```bash
  curl http://localhost:8000/stats?period=week
  # Должна вернуться статистика из БД
  ```

- [ ] Frontend → API → Database
  1. Открыть http://localhost:3000
  2. Dashboard должен показывать данные
  3. Данные должны быть из БД через API

## 🛠️ Проверка Make команд

- [ ] `make docker-up` работает
- [ ] `make docker-down` работает
- [ ] `make docker-restart` работает
- [ ] `make docker-logs` работает
- [ ] `make docker-status` работает
- [ ] `make docker-clean` работает

```bash
# Проверить все команды:
make help | grep docker
```

## 📚 Проверка документации

- [ ] README.md содержит раздел Docker
- [ ] devops/README.md существует и актуален
- [ ] devops/QUICKSTART.md существует
- [ ] devops/doc/sprint-d0-completed.md существует
- [ ] SPRINT-D0-DOCKER-SETUP.md существует

```bash
# Проверить все документы:
ls -la README.md
ls -la devops/README.md
ls -la devops/QUICKSTART.md
ls -la devops/doc/sprint-d0-completed.md
ls -la SPRINT-D0-DOCKER-SETUP.md
```

## ✅ Финальная проверка

Если все пункты отмечены, Sprint D0 успешно завершен! 🎉

### Быстрая проверка всех сервисов:

```bash
# 1. Запустить
make docker-up

# 2. Проверить статус
make docker-status
# Все контейнеры должны быть "Up"

# 3. Проверить логи
make docker-logs
# Не должно быть ошибок

# 4. Проверить API
curl http://localhost:8000/docs
# Должен вернуть HTML

# 5. Проверить Frontend
open http://localhost:3000  # или start для Windows
# Должна открыться страница dashboard

# 6. Проверить Bot
# Отправить /start боту в Telegram
# Должен прийти ответ

# ✅ Все работает!
```

## 🐛 Troubleshooting

Если что-то не работает:

1. **Проверьте логи:**
   ```bash
   make docker-logs
   ```

2. **Проверьте .env файл:**
   ```bash
   cat .env
   ```

3. **Пересоберите образы:**
   ```bash
   docker-compose build --no-cache
   make docker-up
   ```

4. **Очистите и запустите заново:**
   ```bash
   make docker-clean
   make docker-up
   ```

5. **Проверьте порты:**
   ```bash
   netstat -ano | findstr :3000
   netstat -ano | findstr :8000
   ```

## 📊 Итоговый счет

Подсчитайте количество выполненных пунктов:

- Предварительная проверка: __ / 4
- Структура файлов: __ / 7
- Сборка образов: __ / 3
- Запуск контейнеров: __ / 3
- Проверка логов: __ / 3
- Bot: __ / 5
- API: __ / 5
- Frontend: __ / 3
- База данных: __ / 3
- Volumes: __ / 3
- Перезапуск: __ / 3
- Интеграция: __ / 3
- Make команды: __ / 6
- Документация: __ / 5

**Итого: __ / 56**

Если 56/56 - поздравляем! Sprint D0 полностью завершен! 🚀

---

**Дата проверки:** ______________
**Проверил:** ______________
**Статус:** ⬜ Passed / ⬜ Failed



