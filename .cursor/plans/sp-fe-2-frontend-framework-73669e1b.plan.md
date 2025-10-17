<!-- 73669e1b-3031-4b52-ad13-7103cf782e66 acb7edf3-5ce1-47c3-9a37-d84b70061b35 -->
# SP-FE-2: Каркас frontend проекта

## Общая задача

Создать полнофункциональный каркас frontend проекта на базе Next.js, TypeScript, shadcn/ui и Tailwind CSS с настроенными инструментами разработки и качества кода.

## Основные шаги

### 1. Создание ADR и документации

**ADR (Architecture Decision Record)**: Создать `docs/adr/001-frontend-tech-stack.md`

Документировать архитектурное решение о выборе технологического стека:

- **Контекст**: Необходимость выбора технологий для frontend дашборда статистики
- **Решение**: Next.js + TypeScript + shadcn/ui + Tailwind CSS + pnpm
- **Обоснование выбора каждой технологии**:
  - Next.js: SSR/SSG, App Router, оптимизация производительности, SEO-friendly
  - TypeScript: Типобезопасность, лучший DX, раннее обнаружение ошибок
  - shadcn/ui: Кастомизируемые компоненты, Radix UI primitives, доступность
  - Tailwind CSS: Utility-first, быстрая разработка, консистентный дизайн
  - pnpm: Скорость установки, экономия места, строгость зависимостей
- **Альтернативы**: Рассмотренные варианты (Vite, MUI, styled-components, npm/yarn)
- **Последствия**: Влияние на разработку, производительность, поддержку
- **Статус**: Принято

Формат ADR по стандарту: Context → Decision → Consequences

**Technical Vision**: Создать `frontend/doc/front-vision.md`

Разработать техническое видение frontend приложения:

- Описание архитектуры frontend приложения
- Структура компонентов и страниц
- Паттерны работы с API
- Управление состоянием (React hooks / Context API)
- Стратегия стилизации с Tailwind CSS
- Интеграция с Backend API (http://localhost:8000)

### 2. Инициализация Next.js проекта

Создать Next.js проект с TypeScript в директории `frontend/`:

```bash
cd frontend
pnpm create next-app@latest . --typescript --tailwind --eslint --app --src-dir --import-alias "@/*"
```

Конфигурация:

- App Router (новая версия Next.js)
- TypeScript
- Tailwind CSS
- ESLint
- src/ directory
- Import alias `@/*`

### 3. Интеграция shadcn/ui

Инициализировать shadcn/ui:

```bash
cd frontend
pnpm dlx shadcn@latest init
```

Установить базовые компоненты для дашборда:

- card
- button
- input
- label
- tabs
- chart (для графиков)
- table (для данных)
- badge (для трендов)

### 4. Структура проекта

Создать оптимальную структуру директорий в `frontend/src/`:

```
frontend/
├── src/
│   ├── app/              # Next.js App Router
│   │   ├── layout.tsx    # Root layout
│   │   ├── page.tsx      # Главная страница (dashboard)
│   │   └── globals.css   # Глобальные стили
│   ├── components/       # React компоненты
│   │   ├── ui/          # shadcn/ui компоненты (автогенерация)
│   │   ├── dashboard/   # Компоненты дашборда (для SP-FE-3)
│   │   └── chat/        # Компоненты чата (для SP-FE-4)
│   ├── lib/             # Утилиты
│   │   ├── utils.ts     # Вспомогательные функции
│   │   └── api.ts       # API клиент для Backend
│   └── types/           # TypeScript типы
│       └── index.ts     # Типы API responses
├── public/              # Статические файлы
├── doc/                 # Документация
│   ├── frontend-roadmap.md
│   ├── front-vision.md  (новый)
│   └── dashboard_image.jpg
├── .eslintrc.json       # ESLint конфигурация
├── .prettierrc          # Prettier конфигурация
├── next.config.js       # Next.js конфигурация
├── tailwind.config.ts   # Tailwind конфигурация
├── tsconfig.json        # TypeScript конфигурация
├── package.json         # Зависимости
└── pnpm-lock.yaml       # Lock file
```

### 5. Настройка инструментов качества кода

**ESLint**: Расширить конфигурацию для строгой проверки

**Prettier**: Добавить конфигурацию для форматирования

- printWidth: 100
- semi: true
- singleQuote: true
- trailingComma: 'es5'

**TypeScript**: Настроить strict mode

### 6. Настройка API клиента

Создать `frontend/src/lib/api.ts` с базовым клиентом для работы с Backend API:

- Функции для fetch запросов
- Типизация responses согласно API контракту
- Обработка ошибок
- Base URL конфигурация

Создать `frontend/src/types/index.ts` с TypeScript типами на основе API контракта:

```typescript
export interface KPIMetric {
  label: string;
  value: string;
  change: number;
  trend: 'up' | 'down' | 'stable';
}

export interface TimelinePoint {
  date: string;
  value: number;
}

export interface StatsResponse {
  kpi_metrics: KPIMetric[];
  timeline: TimelinePoint[];
}
```

### 7. Базовая страница и layout

Создать минимальный рабочий layout с:

- Responsive дизайн
- Sidebar (заглушка для навигации)
- Header
- Main content area

Главная страница (`page.tsx`):

- Placeholder для дашборда
- Проверка подключения к API (health check)

### 8. Команды в Makefile

Добавить команды для работы с frontend в корневой `Makefile`:

```makefile
# Frontend commands
fe-install:
	cd frontend && pnpm install

fe-dev:
	cd frontend && pnpm dev

fe-build:
	cd frontend && pnpm build

fe-lint:
	cd frontend && pnpm lint

fe-format:
	cd frontend && pnpm format

fe-type-check:
	cd frontend && pnpm type-check

fe-check: fe-lint fe-type-check
	@echo "✅ Frontend checks passed!"
```

### 9. Скрипты в package.json

Добавить необходимые npm scripts:

- `dev` - запуск dev сервера
- `build` - production build
- `start` - запуск production сервера
- `lint` - ESLint проверка
- `format` - Prettier форматирование
- `type-check` - TypeScript проверка

### 10. Конфигурация окружения

Создать `.env.local` для локальной разработки:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Создать `.env.example` с примером переменных.

### 11. Настройка .gitignore

Обновить корневой `.gitignore` проекта, добавив frontend-специфичные исключения:

```gitignore
# Frontend (Next.js)
frontend/.next/
frontend/out/
frontend/build/
frontend/dist/
frontend/.vercel/
frontend/.turbo/

# Dependencies
frontend/node_modules/

# Environment files
frontend/.env*.local
frontend/.env.production

# Debug logs
frontend/npm-debug.log*
frontend/yarn-debug.log*
frontend/yarn-error.log*
frontend/pnpm-debug.log*

# IDE
frontend/.vscode/
frontend/.idea/

# OS
frontend/.DS_Store
frontend/Thumbs.db

# TypeScript
frontend/*.tsbuildinfo
frontend/next-env.d.ts
```

**Важно:** Next.js автоматически создает собственный `.gitignore` в директории `frontend/` при инициализации. Его содержимое корректно и должно быть сохранено. Корневой `.gitignore` дополняется для явности и консистентности с остальным проектом.

## Критерии завершения

- ✅ Next.js проект создан и запускается (`pnpm dev`)
- ✅ shadcn/ui интегрирован, базовые компоненты установлены
- ✅ Tailwind CSS настроен и работает
- ✅ TypeScript strict mode включен
- ✅ ESLint и Prettier настроены
- ✅ Структура директорий создана
- ✅ API клиент с типами реализован
- ✅ Базовый layout и главная страница созданы
- ✅ Makefile команды добавлены и работают
- ✅ Документ front-vision.md создан
- ✅ Dev сервер запускается без ошибок
- ✅ Hot reload работает

## Deliverables

1. Работающий Next.js проект в `frontend/`
2. Документ `frontend/doc/front-vision.md`
3. Настроенные инструменты разработки
4. Makefile команды для frontend
5. Базовый API клиент с типами
6. README.md для frontend с инструкциями

### To-dos

- [ ] Создать frontend/doc/front-vision.md с техническим видением frontend приложения
- [ ] Инициализировать Next.js проект с TypeScript и Tailwind CSS в директории frontend/
- [ ] Интегрировать shadcn/ui и установить базовые компоненты
- [ ] Создать структуру директорий (components/, lib/, types/)
- [ ] Настроить ESLint, Prettier, TypeScript strict mode
- [ ] Создать API клиент и TypeScript типы на основе Backend API контракта
- [ ] Создать базовый layout с sidebar, header и main content area
- [ ] Создать главную страницу с placeholder для дашборда
- [ ] Добавить frontend команды в корневой Makefile (fe-install, fe-dev, fe-build, fe-lint, fe-check)
- [ ] Создать .env.local и .env.example с конфигурацией API_URL
- [ ] Проверить работу dev сервера, hot reload и всех команд качества кода