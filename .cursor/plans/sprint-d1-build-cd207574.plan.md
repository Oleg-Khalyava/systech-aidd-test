<!-- cd207574-de61-4c62-aecf-354f89f3309e 9f0abf86-11c4-4000-9f59-548ba50ab91d -->
# План Спринта D1 - Build & Publish

## Обзор

Настройка автоматической сборки и публикации Docker образов (bot, api, frontend) в GitHub Container Registry через GitHub Actions. Подготовка к спринтам D2 (ручной deploy) и D3 (авто deploy).

## 1. Документация: Введение в GitHub Actions

**Файл:** `devops/doc/github-actions-guide.md`

Создать руководство на русском:

- Основы GitHub Actions и workflow
- Принципы работы с Pull Request
- Trigger events (push, pull_request, workflow_dispatch)
- Matrix strategy для параллельной сборки
- Публикация образов (public vs private)
- Docker layer caching для ускорения

## 2. GitHub Actions Workflow

**Файл:** `.github/workflows/build.yml`

Создать workflow с:

- **Trigger:** 
  - push в ветку `day-6-devops`
  - pull_request в ветку `day-6-devops`
- **Matrix strategy:** 3 образа (bot, api, frontend)
- **Шаги:**

  1. Checkout кода
  2. Docker Buildx setup
  3. Login в ghcr.io через `GITHUB_TOKEN`
  4. Build образов с кешированием layers
  5. Build args (для будущего использования: BUILD_DATE, VERSION)
  6. Tag образов: `latest` и `sha-<commit>`
  7. Push в ghcr.io (только для push, не для PR)

**Теги образов:**

```
ghcr.io/oleg-khalyava/systech-aidd-test-bot:latest
ghcr.io/oleg-khalyava/systech-aidd-test-bot:sha-abc1234
```

**Контексты для сборки:**

- bot/api: context=`.`, dockerfile=`devops/{service}.Dockerfile`
- frontend: context=`./frontend`, dockerfile=`../devops/frontend.Dockerfile`

**Build args:**

- `BUILD_DATE` - дата сборки
- `VERSION` - версия (commit SHA)
- Подготовка для будущего использования в labels

## 3. Docker Compose для Production

**Файл:** `docker-compose.prod.yml`

Создать новый compose файл для использования образов из registry:

- Заменить `build` на `image: ghcr.io/...`
- Сохранить все volumes, ports, env_file
- Использовать tag `latest` по умолчанию
- Добавить возможность override через переменную `IMAGE_TAG`

**Оригинальный:** `docker-compose.yml` (остается для local build)

## 4. Makefile команды

Добавить в `Makefile`:

```makefile
# Production (registry images)
docker-prod-pull:    # Pull образов из registry
docker-prod-up:      # Запуск из registry
docker-prod-down:    # Остановка prod

# Проверка образов
docker-images-list:  # Список локальных образов
```

## 5. Документация: Публичные образы

**Файл:** `devops/doc/github-packages-public.md`

Пошаговая инструкция (со скриншотами/описанием):

1. После первого push образов зайти на GitHub
2. Перейти в Packages репозитория
3. Для каждого образа: Settings → Change visibility → Public
4. Подтвердить публичный доступ
5. Проверка pull без авторизации

## 6. Обновление документации

**Файл:** `devops/README.md`

Добавить секции:

- Badge статуса сборки workflow
- Раздел "Использование образов из Registry"
- Команды для pull и запуска prod версии
- Ссылки на ghcr.io образы

**Файл:** `README.md`

Добавить badge сборки в начало файла.

## 7. DevOps Roadmap

**Файл:** `devops/doc/devops-roadmap.md`

Обновить статус:

- ✅ D0: Basic Docker Setup (завершен)
- 🔄 D1: Build & Publish (в работе)
- 📋 D2: Server Deploy (следующий)
- 📋 D3: Auto Deploy (планируется)

## Ключевые файлы для создания/изменения

1. `.github/workflows/build.yml` - новый
2. `docker-compose.prod.yml` - новый
3. `devops/doc/github-actions-guide.md` - новый
4. `devops/doc/github-packages-public.md` - новый
5. `devops/README.md` - обновить
6. `README.md` - добавить badge
7. `Makefile` - добавить команды
8. `devops/doc/devops-roadmap.md` - обновить статус

## MVP подход - Не включаем

- Lint checks в CI (добавим позже)
- Запуск тестов в CI (добавим позже)
- Security scanning (добавим позже)
- Multi-platform builds (добавим позже)
- Helm charts / Kubernetes (спринты D2/D3)

## Готовность к следующим спринтам

- D2 (Server Deploy): готовые образы в registry для pull на сервер
- D3 (Auto Deploy): workflow уже настроен, добавим только deploy шаги

### To-dos

- [ ] Создать руководство по GitHub Actions (devops/doc/github-actions-guide.md)
- [ ] Создать workflow .github/workflows/build.yml с matrix strategy
- [ ] Создать docker-compose.prod.yml для образов из registry
- [ ] Добавить команды для работы с production образами в Makefile
- [ ] Создать инструкцию по настройке публичных образов (devops/doc/github-packages-public.md)
- [ ] Обновить devops/README.md с badge, registry usage, prod командами
- [ ] Добавить badge статуса сборки в главный README.md
- [ ] Обновить статус спринтов в devops/doc/devops-roadmap.md