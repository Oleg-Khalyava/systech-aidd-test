# GitHub Actions - Руководство по автоматизации сборки

## 📚 Введение

GitHub Actions - это встроенная платформа CI/CD от GitHub, которая позволяет автоматизировать процессы разработки, тестирования и развертывания прямо в вашем репозитории.

### Основные преимущества

- ✅ **Встроенность** - нет необходимости в сторонних сервисах
- ✅ **Бесплатно** - 2000 минут/месяц для приватных репозиториев, безлимит для публичных
- ✅ **Интеграция** - нативная работа с GitHub API и Packages
- ✅ **Мощность** - параллельная сборка, matrix strategy, caching
- ✅ **Простота** - YAML конфигурация, готовые Actions из Marketplace

---

## 🏗️ Основные концепции

### Workflow (Рабочий процесс)

**Workflow** - это автоматизированный процесс, описанный в YAML файле в директории `.github/workflows/`.

```yaml
name: Build Docker Images
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build
        run: docker build .
```

### Jobs (Задачи)

**Job** - это набор шагов (steps), выполняющихся на одном runner'е. Jobs могут выполняться параллельно или последовательно.

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps: [...]

  test:
    needs: build  # зависимость - запустится после build
    runs-on: ubuntu-latest
    steps: [...]
```

### Steps (Шаги)

**Step** - это отдельное действие внутри job'а. Может быть:
- **Action** - готовое действие из Marketplace (`uses:`)
- **Command** - команда shell (`run:`)

```yaml
steps:
  - uses: actions/checkout@v4           # Action
  - run: npm install                     # Command
  - name: Run tests
    run: npm test                        # Command с именем
```

---

## 🎯 Trigger Events (События запуска)

Workflow может запускаться на различные события:

### Push - при пуше в ветку

```yaml
on:
  push:
    branches:
      - main
      - develop
      - 'feature/**'
```

### Pull Request - при создании/обновлении PR

```yaml
on:
  pull_request:
    branches:
      - main
    types: [opened, synchronize, reopened]
```

### Комбинированные триггеры

```yaml
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:  # ручной запуск через UI
```

### Фильтры по путям

```yaml
on:
  push:
    paths:
      - 'src/**'
      - 'Dockerfile'
    paths-ignore:
      - '**.md'
```

---

## 🔄 Работа с Pull Request

### Типичный workflow для PR

1. **Разработчик создает PR** → запускается workflow
2. **CI проверяет код:**
   - Сборка проекта
   - Запуск тестов
   - Проверка линтером
   - Сборка Docker образов
3. **Статус отображается в PR** (✅ Success / ❌ Failed)
4. **Мержинг только после успешной проверки**

### Условное выполнение для PR

```yaml
steps:
  - name: Build only
    run: docker build -t myapp .

  - name: Push to registry
    if: github.event_name != 'pull_request'
    run: docker push myapp
```

**Важно:** Не пушить образы при PR, только собирать и проверять!

### Permissions для PR

```yaml
permissions:
  contents: read        # чтение кода
  packages: write       # запись в GitHub Packages
  pull-requests: write  # комментарии в PR
```

---

## 📦 Matrix Strategy (Параллельная сборка)

Matrix strategy позволяет запустить один job с разными параметрами параллельно.

### Простой пример

```yaml
jobs:
  build:
    strategy:
      matrix:
        service: [bot, api, frontend]
    steps:
      - run: docker build -f ${{ matrix.service }}.Dockerfile
```

Этот job запустится **3 раза параллельно** с разными значениями `service`.

### Расширенный matrix

```yaml
strategy:
  matrix:
    service: [bot, api, frontend]
    include:
      - service: bot
        context: .
        dockerfile: devops/bot.Dockerfile
      - service: api
        context: .
        dockerfile: devops/api.Dockerfile
      - service: frontend
        context: ./frontend
        dockerfile: ../devops/frontend.Dockerfile

steps:
  - name: Build ${{ matrix.service }}
    uses: docker/build-push-action@v5
    with:
      context: ${{ matrix.context }}
      file: ${{ matrix.dockerfile }}
```

### Fail-fast strategy

```yaml
strategy:
  fail-fast: false  # продолжить остальные сборки при ошибке
  matrix:
    service: [bot, api, frontend]
```

---

## 🐳 Сборка и публикация Docker образов

### Полный workflow для Docker

```yaml
name: Build and Push Docker Images

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    strategy:
      matrix:
        service: [bot, api, frontend]

    steps:
      # 1. Checkout кода
      - name: Checkout repository
        uses: actions/checkout@v4

      # 2. Setup Docker Buildx (для advanced features)
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      # 3. Login в GitHub Container Registry
      - name: Log in to the Container registry
        if: github.event_name != 'pull_request'
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      # 4. Генерация метаданных (tags, labels)
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}-${{ matrix.service }}
          tags: |
            type=ref,event=branch
            type=sha,prefix=sha-
            type=raw,value=latest,enable={{is_default_branch}}

      # 5. Build и Push
      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          file: ./devops/${{ matrix.service }}.Dockerfile
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

### Docker Layer Caching

GitHub Actions предоставляет **GitHub Actions Cache** для кеширования Docker layers:

```yaml
- name: Build with cache
  uses: docker/build-push-action@v5
  with:
    cache-from: type=gha          # читать кеш из GHA
    cache-to: type=gha,mode=max   # сохранять все layers
```

**Преимущества:**
- ⚡ Ускорение сборки в 3-10 раз
- 💰 Экономия compute времени
- 🔄 Кеш автоматически инвалидируется при изменениях

---

## 📤 Публикация в GitHub Container Registry

### Public vs Private образы

**Private (по умолчанию):**
- ✅ Безопасно для закрытых проектов
- ❌ Требует авторизации для pull
- ❌ Ограничения на количество pull'ов

**Public:**
- ✅ Доступен без авторизации
- ✅ Безлимитные pull'ы
- ❌ Код образа виден всем

### Как сделать образ публичным

1. После первой публикации образа зайдите на GitHub
2. Перейдите в **Packages** вашего репозитория
3. Выберите образ → **Package settings**
4. **Change visibility** → **Public**
5. Подтвердите действие

### Тегирование образов

```yaml
tags: |
  ghcr.io/username/repo-bot:latest           # latest для основной ветки
  ghcr.io/username/repo-bot:sha-abc1234     # SHA коммита
  ghcr.io/username/repo-bot:v1.0.0          # семантическая версия
  ghcr.io/username/repo-bot:dev             # ветка develop
```

**Best practices:**
- `latest` - только для main/master ветки
- `sha-<commit>` - для отслеживания конкретных сборок
- `v1.0.0` - для релизов (через tags)

---

## ⚡ Оптимизация производительности

### 1. Параллельные jobs

```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    steps: [...]

  test:
    runs-on: ubuntu-latest
    steps: [...]

  build:
    needs: [lint, test]  # запустится только после успеха
    runs-on: ubuntu-latest
    steps: [...]
```

### 2. Кеширование зависимостей

```yaml
- name: Cache pip dependencies
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
```

### 3. Условное выполнение

```yaml
- name: Skip if no changes
  if: contains(github.event.head_commit.message, '[skip ci]')
  run: echo "Skipping CI"
```

### 4. Использование GitHub Cache

```yaml
- name: Cache Docker layers
  uses: actions/cache@v3
  with:
    path: /tmp/.buildx-cache
    key: ${{ runner.os }}-buildx-${{ github.sha }}
    restore-keys: |
      ${{ runner.os }}-buildx-
```

---

## 🔐 Безопасность

### Secrets

Никогда не храните токены в коде! Используйте GitHub Secrets:

```yaml
steps:
  - name: Deploy to production
    env:
      API_TOKEN: ${{ secrets.API_TOKEN }}
    run: ./deploy.sh
```

**Добавление секрета:**
Repository → Settings → Secrets and variables → Actions → New repository secret

### GITHUB_TOKEN

Автоматический токен, доступный в каждом workflow:

```yaml
- name: Login to GHCR
  uses: docker/login-action@v3
  with:
    registry: ghcr.io
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}
```

**Преимущества:**
- ✅ Не требует создания
- ✅ Автоматически expires
- ✅ Минимальные необходимые права

---

## 📊 Мониторинг и отладка

### Статус workflow

**Badge в README:**
```markdown
![Build Status](https://github.com/username/repo/workflows/Build/badge.svg)
```

### Просмотр логов

1. GitHub → Actions → выбрать workflow run
2. Кликнуть на job → раскрыть steps
3. Логи в реальном времени + архив после завершения

### Debug mode

```yaml
- name: Debug info
  run: |
    echo "Event: ${{ github.event_name }}"
    echo "Branch: ${{ github.ref }}"
    echo "SHA: ${{ github.sha }}"
    env
```

---

## 📖 Дополнительные ресурсы

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub Actions Marketplace](https://github.com/marketplace?type=actions)
- [Docker Build Push Action](https://github.com/docker/build-push-action)
- [Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)

---

## 🎯 Следующие шаги

1. ✅ Создать `.github/workflows/build.yml` в вашем проекте
2. ✅ Настроить matrix strategy для сборки образов
3. ✅ Протестировать на PR
4. ✅ Проверить публикацию в ghcr.io
5. ✅ Сделать образы публичными
6. ✅ Добавить badge в README

Удачной автоматизации! 🚀

