# DevOps Roadmap

## Обзор

MVP DevOps roadmap для быстрого развертывания проекта от локальной разработки до автоматического деплоя на удаленный сервер.

## Спринты

| Код | Описание | Статус | Дата | Документация |
|-----|----------|--------|------|--------------|
| D0 | Basic Docker Setup | ✅ Завершен | 18.10.2025 | [sprint-d0-completed.md](sprint-d0-completed.md) |
| D1 | Build & Publish | 🚧 В работе | 18.10.2025 | - |
| D2 | Развертывание на сервер | 📋 Планируется | - | - |
| D3 | Auto Deploy | 📋 Планируется | - | - |

### Легенда статусов

- 📋 Планируется - спринт запланирован
- 🚧 В работе - спринт в процессе выполнения
- ✅ Завершен - спринт выполнен

---

## Спринт D0: Basic Docker Setup ✅

**Статус:** ✅ Завершен
**Дата завершения:** 18.10.2025

### Цели

Запустить все сервисы проекта локально через docker-compose одной командой.

### Выполненные работы

- ✅ Создан простой Dockerfile для каждого сервиса: bot, api, frontend
- ✅ Создан docker-compose.yml с 3 сервисами: Bot, API, Frontend
- ✅ Настроены .dockerignore файлы для всех сервисов
- ✅ Настроены volumes для SQLite базы данных и логов
- ✅ Обновлена документация с инструкциями по запуску через Docker
- ✅ Добавлены Make команды для управления Docker
- ✅ Проверена работоспособность: `docker-compose up` запускает все сервисы

**Сервисы:**
- Bot (Python + UV) - Telegram бот, использует SQLite для хранения данных
- API (Python + UV) - FastAPI сервис для статистики, использует ту же SQLite БД
- Frontend (Next.js + pnpm) - веб-интерфейс, подключается к API

**Результаты:**
- 3 простых Dockerfiles (24-35 строк каждый)
- 6 Make команд для управления Docker
- Полная документация в README.md и devops/README.md
- Все критерии приемки выполнены на 100%

См. полный отчет: [sprint-d0-completed.md](sprint-d0-completed.md)

---

## Спринт D1: Build & Publish 🚧

**Статус:** 🚧 В работе
**Дата начала:** 18.10.2025

### Цели

Автоматическая сборка и публикация Docker образов в GitHub Container Registry при изменениях в ветке `day-6-devops`.

### Состав работ

#### Документация
- ✅ Создано руководство по GitHub Actions (`devops/doc/github-actions-guide.md`)
- ✅ Создана инструкция по настройке публичных образов (`devops/doc/github-packages-public.md`)
- ✅ Обновлен devops/README.md с badge и секциями про registry
- ✅ Добавлен badge статуса сборки в главный README.md
- ✅ Обновлен DevOps Roadmap

#### GitHub Actions
- ✅ Создан workflow `.github/workflows/build.yml`
- ✅ Настроены triggers: push и pull_request в ветку `day-6-devops`
- ✅ Реализована matrix strategy для параллельной сборки 3 образов
- ✅ Настроено Docker layer caching для ускорения сборки
- ✅ Добавлены build args (BUILD_DATE, VERSION)
- ✅ Настроено тегирование: `latest` и `sha-<commit>`

#### Docker Integration
- ✅ Создан `docker-compose.prod.yml` для использования образов из registry
- ✅ Добавлены Makefile команды: `docker-prod-pull`, `docker-prod-up`, и др.
- ✅ Настроена поддержка переменной `IMAGE_TAG` для выбора версии

#### Registry
- ✅ Настроена публикация в GitHub Container Registry (ghcr.io)
- ✅ Образы: `bot`, `api`, `frontend`
- 📋 Ожидается: публикация после первого push
- 📋 Ожидается: настройка публичного доступа через GitHub UI

### Результаты

**Создано файлов:**
- `.github/workflows/build.yml` - GitHub Actions workflow
- `docker-compose.prod.yml` - Docker Compose для production
- `devops/doc/github-actions-guide.md` - руководство по CI/CD
- `devops/doc/github-packages-public.md` - инструкция по публичным образам

**Обновлено:**
- `Makefile` - добавлены команды для production
- `devops/README.md` - badge и секции про registry
- `README.md` - badge статуса сборки
- `devops/doc/devops-roadmap.md` - статусы спринтов

**Образы в Registry:**
```
ghcr.io/oleg-khalyava/systech-aidd-test-bot:latest
ghcr.io/oleg-khalyava/systech-aidd-test-api:latest
ghcr.io/oleg-khalyava/systech-aidd-test-frontend:latest
```

### Следующие шаги

1. Push изменений в ветку `day-6-devops`
2. Дождаться завершения GitHub Actions workflow
3. Настроить публичный доступ к образам через GitHub UI
4. Проверить pull образов без авторизации
5. Протестировать запуск через `docker-compose.prod.yml`

---

## Спринт D2: Развертывание на сервер

### Цели

Развернуть приложение на удаленном сервере с использованием пошаговой инструкции для ручного деплоя.

### Состав работ

- Создать детальную пошаговую инструкцию для ручного развертывания
- Настроить SSH подключение к серверу с использованием SSH ключа
- Подготовить процесс копирования конфигурационных файлов на сервер
- Настроить docker login к GitHub Container Registry
- Реализовать процесс загрузки и запуска образов на сервере
- Создать скрипт проверки работоспособности развернутых сервисов
- Подготовить шаблон production переменных окружения
- Настроить процесс запуска миграций базы данных

---

## Спринт D3: Auto Deploy

### Цели

Автоматизировать процесс развертывания на сервер через GitHub Actions с возможностью ручного запуска.

### Состав работ

- Создать GitHub Actions workflow для автоматического деплоя
- Настроить trigger на ручной запуск (workflow_dispatch)
- Реализовать SSH подключение к серверу из GitHub Actions
- Автоматизировать процесс обновления образов и перезапуска сервисов
- Создать инструкцию по настройке GitHub Secrets
- Добавить уведомления о статусе деплоя
- Обновить README с информацией об автоматическом деплое

---

## Принципы разработки

1. **MVP подход** - фокус на простоте и скорости
2. **Итеративность** - небольшие управляемые спринты
3. **Документация** - каждый спринт должен быть задокументирован
4. **Воспроизводимость** - все процессы должны быть автоматизированы

## Следующие шаги

После завершения MVP DevOps roadmap можно рассмотреть:
- Мониторинг и логирование
- Автоматическое масштабирование
- Backup и disaster recovery
- Security scanning
- Performance optimization

