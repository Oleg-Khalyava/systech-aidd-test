# Техническое видение Frontend приложения

**Дата создания:** 17 октября 2025
**Версия:** 1.0
**Проект:** systech-aidd-test Frontend

## Обзор

Frontend приложение для systech-aidd-test представляет собой современный веб-интерфейс на базе Next.js, предоставляющий администраторам два ключевых инструмента:

1. **Dashboard статистики** - визуализация метрик Telegram бота
2. **ИИ-чат интерфейс** - веб-версия аналитического помощника

## Технологический стек

### Core Technologies

- **Framework:** Next.js 14+ (App Router)
- **Язык:** TypeScript 5+
- **UI Library:** shadcn/ui (Radix UI + Tailwind)
- **Styling:** Tailwind CSS 3+
- **Пакетный менеджер:** pnpm

### Обоснование выбора

Подробное обоснование технологического стека задокументировано в [ADR-001](./adr/001-frontend-tech-stack.md).

## Архитектура приложения

### Общая структура

```
┌─────────────────────────────────────────────────────┐
│              Next.js Frontend (Port 3000)           │
│                                                     │
│  ┌──────────────┐        ┌──────────────┐         │
│  │  Dashboard   │        │   AI Chat    │         │
│  │   Page       │        │    Page      │         │
│  └──────┬───────┘        └──────┬───────┘         │
│         │                       │                  │
│         └───────────┬───────────┘                  │
│                     │                              │
│              ┌──────▼──────┐                       │
│              │ API Client  │                       │
│              │  (lib/api)  │                       │
│              └──────┬──────┘                       │
└─────────────────────┼──────────────────────────────┘
                      │
                      │ HTTP/REST
                      │
┌─────────────────────▼──────────────────────────────┐
│          FastAPI Backend (Port 8000)               │
│                                                    │
│  GET /stats?period=day|week|month                 │
│  POST /chat (планируется в SP-FE-4)               │
└────────────────────────────────────────────────────┘
```

### Структура директорий

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── layout.tsx         # Root layout (общий для всех страниц)
│   │   ├── page.tsx           # Главная страница (dashboard)
│   │   ├── chat/              # Chat страница (SP-FE-4)
│   │   │   └── page.tsx
│   │   └── globals.css        # Глобальные стили
│   │
│   ├── components/            # React компоненты
│   │   ├── ui/               # shadcn/ui компоненты (автогенерация)
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── table.tsx
│   │   │   └── ...
│   │   │
│   │   ├── dashboard/        # Компоненты дашборда
│   │   │   ├── kpi-card.tsx        # KPI метрика
│   │   │   ├── timeline-chart.tsx  # График активности
│   │   │   ├── period-selector.tsx # Переключатель периода
│   │   │   └── stats-grid.tsx      # Сетка метрик
│   │   │
│   │   ├── chat/             # Компоненты чата (SP-FE-4)
│   │   │   ├── message.tsx         # Сообщение
│   │   │   ├── input.tsx           # Поле ввода
│   │   │   └── chat-container.tsx  # Контейнер чата
│   │   │
│   │   └── layout/           # Layout компоненты
│   │       ├── sidebar.tsx         # Боковое меню
│   │       ├── header.tsx          # Шапка
│   │       └── main-layout.tsx     # Основной layout
│   │
│   ├── lib/                  # Утилиты и хелперы
│   │   ├── utils.ts         # Вспомогательные функции
│   │   ├── api.ts           # API клиент для Backend
│   │   └── cn.ts            # classnames utility (shadcn)
│   │
│   └── types/               # TypeScript типы
│       ├── index.ts         # Экспорт всех типов
│       └── api.ts           # Типы API responses
│
├── public/                  # Статические файлы
│   ├── favicon.ico
│   └── images/
│
├── doc/                     # Документация
│   ├── frontend-roadmap.md
│   ├── front-vision.md     # Этот документ
│   └── dashboard_image.jpg  # Референс UI
│
├── .env.local              # Локальные переменные окружения
├── .env.example            # Пример конфигурации
├── .eslintrc.json          # ESLint конфигурация
├── .prettierrc             # Prettier конфигурация
├── next.config.js          # Next.js конфигурация
├── tailwind.config.ts      # Tailwind конфигурация
├── tsconfig.json           # TypeScript конфигурация
├── package.json            # Зависимости и скрипты
└── pnpm-lock.yaml          # Lock file
```

## Компоненты и страницы

### 1. Dashboard (Главная страница)

**Маршрут:** `/`
**Файл:** `src/app/page.tsx`

**Функциональность:**
- Отображение 4 KPI метрик (Total Users, Total Messages, Deleted Messages, Avg Message Length)
- График активности (timeline chart)
- Переключатель периода (day/week/month)
- Автообновление данных каждые 30 секунд

**Компоненты:**
```tsx
<Dashboard>
  <PeriodSelector />
  <StatsGrid>
    <KPICard /> × 4
  </StatsGrid>
  <TimelineChart />
</Dashboard>
```

**Источник данных:** `GET /stats?period=week`

### 2. AI Chat (Аналитический помощник)

**Маршрут:** `/chat`
**Файл:** `src/app/chat/page.tsx`

**Функциональность (SP-FE-4):**
- Интерфейс чата с ИИ
- История сообщений
- Streaming responses (опционально)
- Markdown support для ответов

**Компоненты:**
```tsx
<ChatPage>
  <ChatContainer>
    <Message /> × N
  </ChatContainer>
  <ChatInput />
</ChatPage>
```

**Источник данных:** `POST /chat` (планируется)

### 3. Layout компоненты

**Sidebar** - навигационное меню:
- Dashboard (активен по умолчанию)
- AI Chat (SP-FE-4)
- Будущие разделы

**Header** - шапка приложения:
- Логотип/название проекта
- Breadcrumbs навигация
- Опционально: user menu

## Паттерны работы с API

### API клиент (`src/lib/api.ts`)

Базовая реализация fetch-обертки для работы с Backend API:

```typescript
// Типы из API контракта
import { StatsResponse } from '@/types/api';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  async get<T>(endpoint: string): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`);
    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }
    return response.json();
  }

  // Метод для получения статистики
  async getStats(period: 'day' | 'week' | 'month' = 'week'): Promise<StatsResponse> {
    return this.get<StatsResponse>(`/stats?period=${period}`);
  }
}

export const apiClient = new ApiClient(API_BASE_URL);
```

### Обработка ошибок

Все API запросы оборачиваются в try-catch с user-friendly сообщениями:

```typescript
try {
  const data = await apiClient.getStats('week');
  // Обработка данных
} catch (error) {
  console.error('Failed to fetch stats:', error);
  // Показать toast/notification пользователю
}
```

### Стратегия загрузки данных

1. **Dashboard статистика:**
   - Client-side fetching с React hooks (useState, useEffect)
   - Loading states
   - Error boundaries
   - Периодическое обновление каждые 30 секунд

2. **Будущие улучшения (опционально):**
   - React Query для кэширования и автообновления
   - SWR для revalidation
   - Optimistic updates

## Управление состоянием

### Подход

Используем **встроенные React инструменты** без дополнительных библиотек:

1. **Local state (useState)** - для UI состояния компонентов
2. **Context API** - для глобального состояния (если понадобится)
3. **URL state** - для фильтров и параметров (useSearchParams)

### Пример: Dashboard state

```typescript
// src/app/page.tsx
export default function DashboardPage() {
  const [period, setPeriod] = useState<'day' | 'week' | 'month'>('week');
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Загрузка данных при изменении периода
    fetchStats();
  }, [period]);

  // ...
}
```

### Когда использовать Context API

Context API понадобится если:
- Глобальные настройки (theme, language)
- Данные пользователя (в будущем, если будет auth)
- Общие данные между Dashboard и Chat

## Стратегия стилизации

### Tailwind CSS Utility-first

Используем Tailwind классы напрямую в компонентах:

```tsx
<div className="flex flex-col gap-4 p-6 bg-white rounded-lg shadow-md">
  <h2 className="text-2xl font-bold text-gray-900">Dashboard</h2>
  {/* ... */}
</div>
```

### Кастомная конфигурация Tailwind

`tailwind.config.ts`:
```typescript
export default {
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#...',
          // ... color palette
        },
      },
      spacing: {
        // custom spacing if needed
      },
    },
  },
};
```

### CSS Modules для сложных случаев

Используем только если:
- Сложная анимация
- Динамические стили, которые неудобно в Tailwind
- Специфичная логика стилей

### shadcn/ui компоненты

Компоненты shadcn/ui уже используют Tailwind и кастомизируются через:
- Изменение исходного кода компонента (в `components/ui/`)
- CSS переменные для темизации (в `globals.css`)

## Интеграция с Backend API

### API контракт

Backend API (FastAPI) на `http://localhost:8000`:

**Endpoint:** `GET /stats`

**Query параметры:**
- `period`: `day` | `week` | `month` (default: `week`)

**Response:**
```typescript
interface StatsResponse {
  kpi_metrics: KPIMetric[];
  timeline: TimelinePoint[];
}

interface KPIMetric {
  label: string;        // "Total Users"
  value: string;        // "1,234"
  change: number;       // 12.5
  trend: 'up' | 'down' | 'stable';
}

interface TimelinePoint {
  date: string;         // "2025-10-17" (ISO format)
  value: number;        // 523
}
```

### TypeScript типы

Все типы API хранятся в `src/types/api.ts` и экспортируются через `src/types/index.ts`.

### Environment variables

```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Важно:** Переменные с префиксом `NEXT_PUBLIC_` доступны в браузере.

## Качество кода и инструменты

### ESLint

Конфигурация `.eslintrc.json`:
- Next.js рекомендуемые правила
- TypeScript strict правила
- React hooks правила
- Import sorting

### Prettier

Конфигурация `.prettierrc`:
```json
{
  "printWidth": 100,
  "semi": true,
  "singleQuote": true,
  "trailingComma": "es5",
  "tabWidth": 2
}
```

### TypeScript

`tsconfig.json` - strict mode включен:
```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true
  }
}
```

### Команды проверки

```bash
# Линтинг
pnpm lint

# Форматирование
pnpm format

# Проверка типов
pnpm type-check

# Все проверки
pnpm check
```

## Development процесс

### Запуск dev сервера

```bash
# Из корня проекта
make fe-dev

# Или из frontend/
pnpm dev
```

Dev сервер доступен на `http://localhost:3000`

### Hot Module Replacement (HMR)

Next.js автоматически перезагружает компоненты при изменениях:
- Изменения в компонентах - instant update
- Изменения в layout - full reload
- Изменения в конфигурации - restart сервера

### Workflow разработки

1. Создать/изменить компонент
2. Проверить в браузере (HMR)
3. Запустить линтер: `pnpm lint`
4. Запустить type-check: `pnpm type-check`
5. Отформатировать: `pnpm format`
6. Commit изменений

## Production Build

### Сборка приложения

```bash
# Из корня проекта
make fe-build

# Или из frontend/
pnpm build
```

### Запуск production сервера

```bash
pnpm start
```

### Оптимизации Next.js

Автоматически применяются:
- Code splitting по маршрутам
- Tree shaking
- Image optimization
- Font optimization
- CSS minification
- JS minification и compression

## Deployment стратегия

### Docker (планируется)

Dockerfile для frontend:
```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN npm install -g pnpm && pnpm install
COPY . .
RUN pnpm build

FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package.json ./
RUN npm install -g pnpm && pnpm install --prod
EXPOSE 3000
CMD ["pnpm", "start"]
```

### Docker Compose интеграция

```yaml
services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
    depends_on:
      - backend
```

## Roadmap и будущие улучшения

### SP-FE-3: Реализация Dashboard

- Полная реализация KPI cards
- Интеграция графиков (recharts или Chart.js)
- Responsive design
- Loading states и error handling

### SP-FE-4: Реализация ИИ-чата

- Chat UI компоненты
- WebSocket/SSE для real-time (опционально)
- Markdown rendering для ответов
- Сохранение истории чата

### SP-FE-5: Переход на Real API

- Интеграция с RealStatCollector
- Аутентификация (если потребуется)
- Обработка edge cases
- Performance оптимизации

### Будущие возможности

- **Темная тема** - через CSS переменные Tailwind
- **Интернационализация (i18n)** - next-intl
- **Анимации** - Framer Motion
- **Testing** - Jest + React Testing Library
- **E2E тесты** - Playwright
- **Analytics** - Vercel Analytics или custom

## Связанные документы

- [ADR-001: Технологический стек](./adr/001-frontend-tech-stack.md)
- [Frontend Roadmap](./frontend-roadmap.md)
- [Backend Vision](../../docs/vision.md)
- [API Documentation](../../api/README.md)

## Контакты и поддержка

- **Документация Next.js:** https://nextjs.org/docs
- **Документация shadcn/ui:** https://ui.shadcn.com/
- **Референс дизайна:** https://ui.shadcn.com/view/dashboard-01
- **Tailwind CSS:** https://tailwindcss.com/docs

