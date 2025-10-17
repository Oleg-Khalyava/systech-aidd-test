# Frontend - systech-aidd Dashboard

Веб-интерфейс для дашборда статистики Telegram бота и ИИ-чата.

## Технологический стек

- **Framework:** Next.js 14+ (App Router)
- **Язык:** TypeScript
- **UI Library:** shadcn/ui (Radix UI + Tailwind)
- **Styling:** Tailwind CSS
- **Пакетный менеджер:** pnpm

## Быстрый старт

### 1. Установка зависимостей

```bash
# Из корня проекта
make fe-install

# Или из директории frontend
pnpm install
```

### 2. Настройка окружения

Создайте `.env.local` файл (или используйте существующий):

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Запуск dev сервера

```bash
# Из корня проекта
make fe-dev

# Или из директории frontend
pnpm dev
```

Приложение будет доступно на **http://localhost:3000**

### 4. Запустите Backend API

Для работы dashboard нужен запущенный Backend API:

```bash
# В другом терминале
make api-run
```

API будет доступен на **http://localhost:8000**

## Доступные команды

### Из корня проекта (через Makefile)

```bash
make fe-install      # Установить зависимости
make fe-dev          # Запустить dev сервер
make fe-build        # Собрать production build
make fe-lint         # Запустить ESLint
make fe-format       # Отформатировать код Prettier
make fe-type-check   # Проверить типы TypeScript
make fe-check        # Запустить все проверки
```

### Из директории frontend (через pnpm)

```bash
pnpm dev             # Запустить dev сервер
pnpm build           # Собрать production build
pnpm start           # Запустить production сервер
pnpm lint            # Запустить ESLint
pnpm format          # Отформатировать код Prettier
pnpm format:check    # Проверить форматирование
pnpm type-check      # Проверить типы TypeScript
pnpm check           # Запустить все проверки
```

## Структура проекта

```
frontend/
├── src/
│   ├── app/              # Next.js App Router
│   │   ├── layout.tsx    # Root layout
│   │   ├── page.tsx      # Dashboard (главная страница)
│   │   └── globals.css   # Глобальные стили
│   ├── components/       # React компоненты
│   │   ├── ui/          # shadcn/ui компоненты
│   │   ├── dashboard/   # Компоненты дашборда (SP-FE-3)
│   │   ├── chat/        # Компоненты чата (SP-FE-4)
│   │   └── layout/      # Layout компоненты
│   ├── lib/             # Утилиты
│   │   ├── utils.ts     # Вспомогательные функции
│   │   └── api.ts       # API клиент
│   └── types/           # TypeScript типы
│       ├── api.ts       # API типы
│       └── index.ts     # Экспорт типов
├── public/              # Статические файлы
├── doc/                 # Документация
│   ├── frontend-roadmap.md
│   ├── front-vision.md
│   └── dashboard_image.jpg
├── .env.local           # Локальные переменные (не в git)
├── .env.example         # Пример конфигурации
├── package.json         # Зависимости
└── README.md            # Этот файл
```

## Разработка

### Hot Module Replacement

Next.js автоматически перезагружает компоненты при изменениях:
- Изменения компонентов - мгновенное обновление
- Изменения layout - полная перезагрузка
- Изменения конфигурации - перезапуск сервера

### Workflow

1. Внести изменения в код
2. Проверить в браузере (http://localhost:3000)
3. Запустить линтер: `pnpm lint`
4. Проверить типы: `pnpm type-check`
5. Отформатировать: `pnpm format`
6. Commit изменений

### Добавление новых shadcn/ui компонентов

```bash
cd frontend
pnpm dlx shadcn@latest add <component-name>
```

Примеры:
```bash
pnpm dlx shadcn@latest add dialog
pnpm dlx shadcn@latest add dropdown-menu
pnpm dlx shadcn@latest add toast
```

## API Интеграция

### API клиент

Используйте `apiClient` из `@/lib/api`:

```typescript
import { getStats } from '@/lib/api';

const stats = await getStats('week');
```

### TypeScript типы

Все типы API доступны из `@/types`:

```typescript
import type { StatsResponse, KPIMetric, Period } from '@/types';
```

### Обработка ошибок

```typescript
import { ApiError } from '@/lib/api';

try {
  const data = await getStats('week');
} catch (error) {
  if (error instanceof ApiError) {
    console.error('API Error:', error.message, error.status);
  }
}
```

## Production Build

### Сборка

```bash
make fe-build
# или
pnpm build
```

### Запуск production сервера

```bash
pnpm start
```

Production сервер будет доступен на **http://localhost:3000**

## Roadmap

### ✅ SP-FE-2: Каркас frontend проекта (Завершен)

- Next.js проект инициализирован
- shadcn/ui компоненты установлены
- Базовый layout создан
- API клиент готов

### 📋 SP-FE-3: Реализация dashboard (Следующий)

- KPI карточки с данными
- Timeline графики
- Responsive дизайн
- Интеграция с Mock API

### 📋 SP-FE-4: Реализация ИИ-чата

- Chat UI компоненты
- WebSocket/SSE интеграция
- Markdown rendering

### 📋 SP-FE-5: Переход на Real API

- Интеграция с production БД
- Аутентификация
- Performance оптимизация

## Документация

- [Frontend Roadmap](doc/frontend-roadmap.md) - план развития frontend
- [Technical Vision](doc/front-vision.md) - техническое видение
- [ADR-001](doc/adr/001-frontend-tech-stack.md) - обоснование выбора стека
- [SP-FE-2 Summary](doc/sprints/sp-fe-2-summary.md) - итоги спринта 2
- [Next.js Docs](https://nextjs.org/docs) - официальная документация
- [shadcn/ui](https://ui.shadcn.com/) - UI компоненты

## Troubleshooting

### Dev сервер не запускается

```bash
# Переустановите зависимости
rm -rf node_modules pnpm-lock.yaml
pnpm install
```

### API недоступен

```bash
# Проверьте, запущен ли Backend API
make api-run

# Проверьте переменную окружения
cat .env.local
```

### Ошибки TypeScript

```bash
# Запустите type-check для полной информации
pnpm type-check
```

## Лицензия

Этот проект является частью systech-aidd-test.
