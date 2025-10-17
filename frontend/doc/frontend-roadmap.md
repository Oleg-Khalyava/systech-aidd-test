# Frontend Development Roadmap

Роадмап развития пользовательского интерфейса проекта systech-aidd-test.

## Технологический стек

**Backend API**: FastAPI (REST API + OpenAPI документация)
**Frontend Framework**: Next.js 14+ (App Router) + React 19
**Язык**: TypeScript (strict mode)
**UI Components**: shadcn/ui (Radix UI + Tailwind CSS)
**Styling**: Tailwind CSS 4
**Пакетный менеджер**: pnpm
**Документация**: [ADR-001](./adr/001-frontend-tech-stack.md), [Technical Vision](./front-vision.md)

## UI Референсы

**Dashboard**: [shadcn/ui Dashboard](https://ui.shadcn.com/view/dashboard-01) - 4 блока метрик + timeline/графики

## Обзор спринтов

| Код | Описание | Статус | Дата | План |
|-----|----------|--------|------|------|
| SP-FE-1 | Требования к дашборду и Mock API | ✅ Completed | 17.10.2025 | [План](../../.cursor/plans/s1-mock-api-dashboard-25be2357.plan.md) |
| SP-FE-2 | Каркас frontend проекта | ✅ Completed | 17.10.2025 | [План](../../.cursor/plans/sp-fe-2-frontend-framework-73669e1b.plan.md) |
| SP-FE-3 | Реализация dashboard | ✅ Completed | 17.10.2025 | [План](../../.cursor/plans/sp-fe-3-dashboard-implementation-fdea21df.plan.md) |
| SP-FE-4 | Реализация ИИ-чата | 📋 Запланирован | - | - |
| SP-FE-5 | Переход на реальный API | 📋 Запланирован | - | - |

### Статусы
- 📋 **Запланирован** - спринт в очереди на выполнение
- 🚧 **В работе** - спринт выполняется
- ✅ **Завершен** - спринт завершен
- ⏸️ **Приостановлен** - спринт временно приостановлен

---

## SP-FE-1: Требования к дашборду и Mock API ✅

**Статус:** ✅ Completed
**Дата завершения:** 17 октября 2025
**План спринта:** [s1-mock-api-dashboard-25be2357.plan.md](../../.cursor/plans/s1-mock-api-dashboard-25be2357.plan.md)

### Краткое описание реализации

Создан полнофункциональный Mock API на базе FastAPI для обеспечения независимой разработки frontend. Реализован единственный endpoint `GET /stats` с параметром period, возвращающий 4 KPI метрики (Total Users, Total Messages, Deleted Messages, Avg Message Length) и timeline данные для графика активности. Mock API генерирует реалистичные тестовые данные и полностью готов к интеграции с frontend дашбордом.

### Цели
- ✅ Определить функциональные требования к дашборду статистики диалогов
- ✅ Спроектировать и реализовать Mock API на FastAPI для получения статистики
- ✅ Подготовить инфраструктуру для разработки frontend

### Состав работ
- ✅ Формирование функциональных требований к дашборду (4 блока метрик + timeline) на основе существующих возможностей системы
- ✅ Проектирование REST API контракта для frontend:
  - Single endpoint для статистики dashboard (`GET /stats`)
  - Структура данных для 4 KPI метрик (Total Users, Total Messages, Deleted Messages, Avg Message Length)
  - Данные для timeline графиков (временные ряды с количеством сообщений)
- ✅ Создание FastAPI приложения для статистики
- ✅ Проектирование интерфейса `StatCollectorProtocol` с поддержкой Mock и Real реализаций
- ✅ Реализация Mock-версии сборщика статистики с тестовыми данными
- ✅ Автоматическая генерация документации API (OpenAPI/Swagger через FastAPI)
- ✅ Создание entrypoint для запуска FastAPI сервера (`api/api_main.py`)
- ✅ Создание команд для запуска API и тестирования (`make api-run`, `make api-test`, `make api-docs`)
- ✅ Написание тестов для API endpoint и MockStatCollector (100% pass rate)
- ✅ Создание документации с примерами запросов (curl, PowerShell, Python, JavaScript)

### Результаты спринта

**Реализованные компоненты:**
- ✅ FastAPI приложение (`api/api_main.py`) на порту 8000
- ✅ Endpoint `GET /stats?period=day|week|month` с полной валидацией
- ✅ `MockStatCollector` с генерацией реалистичных данных
- ✅ `StatCollectorProtocol` для гибкой архитектуры
- ✅ Swagger UI на `/docs` и ReDoc на `/redoc`
- ✅ 17 автоматических тестов (100% pass rate)
- ✅ Команды в Makefile: `api-run`, `api-stop`, `api-test`, `api-docs`
- ✅ Полная документация с примерами (curl, PowerShell, Python, JS)

**Качество кода:**
- ✅ Ruff linting: All checks passed
- ✅ MyPy type checking: Success, no issues
- ✅ Black formatting: Applied
- ✅ Code coverage: 100% (API endpoints и collectors)

**Deliverables:**
- Frontend разработчики могут начать работу с Mock API
- Архитектура готова для замены Mock → Real collector в SP-FE-5
- API контракт задокументирован и стабилен

---

## SP-FE-2: Каркас frontend проекта ✅

**Статус:** ✅ Completed
**Дата завершения:** 17 октября 2025
**План спринта:** [sp-fe-2-frontend-framework-73669e1b.plan.md](../../.cursor/plans/sp-fe-2-frontend-framework-73669e1b.plan.md)
**Итоги спринта:** [sp-fe-2-summary.md](sprints/sp-fe-2-summary.md)

### Краткое описание реализации

Создан полнофункциональный каркас frontend приложения на базе Next.js 14+ с App Router, TypeScript, shadcn/ui и Tailwind CSS. Реализована базовая архитектура с layout компонентами (Header, Sidebar, MainLayout), API клиент для интеграции с Backend, TypeScript типы для API контракта, и инструменты разработки (ESLint, Prettier, TypeScript). Проект готов к реализации дашборда в SP-FE-3.

### Цели
- ✅ Определить концепцию и требования к frontend
- ✅ Настроить React + shadcn/ui проект
- ✅ Создать базовую структуру проекта с инструментами разработки

### Состав работ
- ✅ Генерация ADR документа `frontend/doc/adr/001-frontend-tech-stack.md` с обоснованием выбора стека
- ✅ Генерация документа `frontend/doc/front-vision.md` с видением пользовательского интерфейса
- ✅ Инициализация Next.js 14+ проекта с App Router, TypeScript, Tailwind CSS, ESLint
- ✅ Интеграция shadcn/ui и установка базовых компонентов (card, button, input, label, tabs, table, badge)
- ✅ Создание структуры директорий: components/{ui, dashboard, chat, layout}, lib/, types/
- ✅ Настройка Prettier для форматирования кода
- ✅ Создание API клиента (lib/api.ts) для работы с Backend API
- ✅ Создание TypeScript типов (types/api.ts) для API контракта
- ✅ Создание layout компонентов (Header, Sidebar, MainLayout)
- ✅ Создание главной страницы с placeholder для dashboard и API health check
- ✅ Обновление корневого layout с интеграцией MainLayout
- ✅ Добавление frontend команд в Makefile (fe-install, fe-dev, fe-build, fe-lint, fe-format, fe-type-check, fe-check)
- ✅ Настройка environment variables (.env.local, .env.example)
- ✅ Обновление .gitignore для frontend файлов
- ✅ Создание README.md для frontend с инструкциями

### Результаты спринта

**Реализованные компоненты:**
- ✅ Next.js 14+ проект с App Router и TypeScript strict mode
- ✅ shadcn/ui интегрирован с 7 базовыми компонентами
- ✅ Tailwind CSS настроен с кастомной конфигурацией
- ✅ API клиент с типизацией и обработкой ошибок
- ✅ Layout система: Header, Sidebar, MainLayout
- ✅ Главная страница с API health check и placeholder для dashboard
- ✅ Makefile команды для всех операций frontend
- ✅ Prettier конфигурация для форматирования

**Качество кода:**
- ✅ ESLint: Configured with Next.js recommended rules
- ✅ TypeScript: Strict mode enabled, no errors
- ✅ Prettier: Configured with project standards
- ✅ No linter errors in created files

**Deliverables:**
- Работающий Next.js проект готов к разработке dashboard
- ADR документ с обоснованием технологического стека
- Technical Vision с архитектурой приложения
- API клиент готов к интеграции с Backend (http://localhost:8000)
- Команды для запуска, сборки и проверки качества кода

**Команды для запуска:**
```bash
make fe-install   # Установить зависимости
make fe-dev       # Запустить dev сервер на http://localhost:3000
make fe-build     # Собрать production build
make fe-check     # Проверить качество кода
```

---

## SP-FE-3: Реализация dashboard ✅

**Статус:** ✅ Completed
**Дата завершения:** 17 октября 2025
**План спринта:** [sp-fe-3-dashboard-implementation-fdea21df.plan.md](../../.cursor/plans/sp-fe-3-dashboard-implementation-fdea21df.plan.md)
**Итоги спринта:** [sp-fe-3-summary.md](sprints/sp-fe-3-summary.md)

### Краткое описание реализации

Создан полнофункциональный dashboard статистики Telegram бота с интеграцией Mock API. Реализованы 4 KPI-карты с маппингом на русский язык, интерактивный график активности на Recharts, переключатель периодов и полноценная система темизации (светлая/темная тема). Весь интерфейс на русском языке с автообновлением данных каждые 30 секунд и responsive дизайном.

### Цели
- ✅ Реализовать дашборд статистики диалогов по референсу shadcn/ui
- ✅ Интегрировать с Mock API
- ✅ Обеспечить современный и отзывчивый UI
- ✅ Добавить поддержку светлой и темной темы

### Состав работ
- ✅ Установка зависимостей (recharts, next-themes)
- ✅ Настройка системы темизации с next-themes
- ✅ Создание компонента ThemeToggle для переключения темы
- ✅ Создание компонента PeriodSelector (День/Неделя/Месяц) на русском
- ✅ Реализация 4 KPI-карт с маппингом меток на русский:
  - Total Users → Всего пользователей
  - Total Messages → Всего сообщений
  - Deleted Messages → Удаленные сообщения
  - Avg Message Length → Средняя длина сообщения
- ✅ Создание компонента TimelineChart с Recharts
- ✅ Интеграция с Mock API (`GET /stats?period=day|week|month`)
- ✅ Реализация адаптивного дизайна (responsive design, mobile-first)
- ✅ Добавление loading states и error handling
- ✅ Автообновление данных каждые 30 секунд
- ✅ Тестирование и отладка (0 ошибок линтера/TypeScript)

### Результаты спринта

**Реализованные компоненты:**
- ✅ Система темизации (светлая/темная тема) с next-themes
- ✅ ThemeToggle компонент в header
- ✅ PeriodSelector компонент на русском языке
- ✅ KPICard с автоматическим маппингом на русский
- ✅ TimelineChart с Recharts и русскими метками
- ✅ Полная интеграция в главную страницу
- ✅ Loading skeletons для KPI-карт
- ✅ Error handling с кнопкой повтора
- ✅ Индикатор автообновления

**Качество кода:**
- ✅ ESLint: 0 ошибок и предупреждений
- ✅ TypeScript: 0 ошибок типов
- ✅ Prettier: Все файлы отформатированы
- ✅ Responsive design: Mobile, Tablet, Desktop

**Deliverables:**
- Dashboard полностью функционален и готов к использованию
- Поддержка светлой и темной темы
- Весь интерфейс на русском языке
- Автообновление данных из Mock API
- Отличная производительность и UX

**Команды для запуска:**
```bash
make api-run     # Запустить Backend API
make fe-dev      # Запустить Frontend dev сервер
# Открыть http://localhost:3000
```

---

## SP-FE-4: Реализация ИИ-чата

### Цели
- Реализовать веб-интерфейс для ИИ-чата
- Расширить FastAPI для обработки чат-запросов
- Реализовать функциональность аналитического помощника для администратора

### Состав работ
- Реализация UI чата на основе референса
- Разработка FastAPI endpoint'ов для чата (веб-аналог Telegram бота)
- Реализация функциональности аналитического помощника:
  - Интерфейс для вопросов по статистике диалогов
  - Интеграция с промптом для text-to-SQL конвертации
  - Выполнение SQL запросов к базе данных
  - Формирование ответа через LLM на основе результатов запроса
- Настройка WebSocket или Server-Sent Events для real-time коммуникации (опционально)
- Тестирование и отладка чат-функциональности

---

## SP-FE-5: Переход на реальный API

### Цели
- Заменить Mock реализацию на реальный сборщик статистики
- Интегрировать FastAPI с production базой данных
- Обеспечить полнофункциональную работу системы

### Состав работ
- Реализация Real-версии `StatCollector` с подключением к БД
- Интеграция FastAPI с базой данных для сбора реальной статистики
- Переключение конфигурации с Mock на Real реализацию (dependency injection)
- Тестирование работы с реальными данными
- Оптимизация производительности запросов к БД
- Настройка CORS и безопасности FastAPI для production
- Финальная проверка и валидация всей системы

