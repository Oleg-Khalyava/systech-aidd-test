<!-- fdea21df-1185-4791-a0a4-5071b83f2c2f b3e217da-d120-47f4-8fa9-a8d26cdfc6ad -->
# SP-FE-3: Реализация Dashboard

## Обзор

Реализовать полнофункциональный dashboard статистики на основе референса shadcn/ui dashboard-01. Интегрировать с Mock API (`GET /stats`), создать компоненты для KPI-метрик и timeline графика. Весь интерфейс на русском языке.

## Ключевые файлы

- `frontend/src/app/page.tsx` - главная страница dashboard (обновить)
- `frontend/src/components/dashboard/kpi-card.tsx` - компонент KPI-карты (создать)
- `frontend/src/components/dashboard/timeline-chart.tsx` - компонент графика (создать)
- `frontend/src/components/dashboard/period-selector.tsx` - переключатель периода (создать)
- `frontend/src/lib/api.ts` - API клиент (уже готов)
- `frontend/src/types/api.ts` - типы API (уже готовы)

## Технические решения

**Charting library:** Recharts (легкий, декларативный, React-friendly)

**Дизайн:** Поддержка светлой и темной темы с переключателем

**Язык интерфейса:** Полностью на русском языке

**Responsive:** Mobile-first подход с Tailwind breakpoints

**Темизация:** Next.js next-themes для управления темой + CSS variables

## Этапы реализации

### 1. Установка зависимостей

Установить Recharts для графиков:

```bash
cd frontend && pnpm add recharts
```

### 2. Создание компонента PeriodSelector

Файл: `frontend/src/components/dashboard/period-selector.tsx`

Компонент с кнопками для выбора периода (День/Неделя/Месяц), использует shadcn/ui Tabs или Button group. Коллбэк для изменения выбранного периода.

### 3. Создание компонента KPICard

Файл: `frontend/src/components/dashboard/kpi-card.tsx`

Отображает одну KPI-метрику:

- Заголовок метрики (label)
- Большое значение (value) 
- Процент изменения (change) с цветовой индикацией
- Иконка тренда (↑↓→) в зависимости от trend
- Использует shadcn/ui Card компонент

Пример структуры:

```tsx
<Card>
  <CardHeader>
    <CardDescription>{label}</CardDescription>
    <CardTitle className="text-3xl">{value}</CardTitle>
  </CardHeader>
  <CardContent>
    <div className={trend === 'up' ? 'text-green-600' : 'text-red-600'}>
      {trend === 'up' ? '↑' : '↓'} {Math.abs(change)}%
    </div>
  </CardContent>
</Card>
```

### 4. Создание компонента TimelineChart

Файл: `frontend/src/components/dashboard/timeline-chart.tsx`

График активности с использованием Recharts:

- Area chart или Line chart
- Данные из `timeline` массива API response
- Responsive дизайн
- Tooltips для детализации
- Русские метки осей

Использует: `<AreaChart>`, `<Area>`, `<XAxis>`, `<YAxis>`, `<Tooltip>`, `<ResponsiveContainer>`

### 5. Обновление главной страницы

Файл: `frontend/src/app/page.tsx`

Интегрировать все компоненты:

```tsx
'use client';

import { useEffect, useState } from 'react';
import { getStats } from '@/lib/api';
import type { StatsResponse, Period } from '@/types';
import { PeriodSelector } from '@/components/dashboard/period-selector';
import { KPICard } from '@/components/dashboard/kpi-card';
import { TimelineChart } from '@/components/dashboard/timeline-chart';

export default function DashboardPage() {
  const [period, setPeriod] = useState<Period>('week');
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Загрузка данных при изменении периода
  useEffect(() => {
    fetchData();
    // Автообновление каждые 30 секунд
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, [period]);

  async function fetchData() {
    try {
      setLoading(true);
      const data = await getStats(period);
      setStats(data);
      setError(null);
    } catch (err) {
      setError('Ошибка загрузки данных');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Дашборд</h1>
          <p className="text-gray-600">Статистика Telegram бота</p>
        </div>
        <PeriodSelector value={period} onChange={setPeriod} />
      </div>

      {/* KPI Metrics Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats?.kpi_metrics.map((metric) => (
          <KPICard key={metric.label} {...metric} />
        ))}
      </div>

      {/* Timeline Chart */}
      <TimelineChart data={stats?.timeline || []} loading={loading} />
    </div>
  );
}
```

### 6. Маппинг меток на русский язык

Метрики из API приходят на английском, нужен маппинг:

- "Total Users" → "Всего пользователей"
- "Total Messages" → "Всего сообщений"  
- "Deleted Messages" → "Удаленные сообщения"
- "Avg Message Length" → "Средняя длина сообщения"

Создать хелпер или использовать словарь в KPICard компоненте.

### 7. Loading и Error states

Добавить состояния загрузки и ошибок:

- Skeleton компоненты для KPI-карт при загрузке
- Error message с кнопкой повторной попытки
- Индикатор автообновления

### 8. Responsive дизайн

Использовать Tailwind breakpoints:

- Mobile (default): 1 колонка
- Tablet (md): 2 колонки для KPI
- Desktop (lg): 4 колонки для KPI
- График всегда на полную ширину

### 9. Тестирование

- Запустить API: `make api-run`
- Запустить frontend: `make fe-dev`
- Проверить работу с разными периодами
- Проверить responsive на разных экранах
- Проверить автообновление (подождать 30 сек)
- Проверить error handling (выключить API)

### 10. Code quality checks

Запустить все проверки:

```bash
make fe-check  # lint + type-check + format
```

Убедиться в отсутствии ошибок линтера и TypeScript.

## Референс дизайна

По скриншоту `dashboard_image.jpg`:

- 4 KPI-карты в ряд (темный фон, светлые карты)
- Большие числа для значений
- Проценты изменения с цветом
- График активности с multiple линиями
- Кнопки выбора периода справа вверху

Адаптируем под светлую тему проекта, сохраняя структуру и пропорции.

## API Integration

Mock API уже работает на `http://localhost:8000`:

**Endpoint:** `GET /stats?period=day|week|month`

**Response:**

```json
{
  "kpi_metrics": [
    {
      "label": "Total Users",
      "value": "1,234",
      "change": 12.5,
      "trend": "up"
    }
  ],
  "timeline": [
    {"date": "2025-10-17", "value": 523}
  ]
}
```

API клиент и типы уже готовы в SP-FE-2.

## Результат спринта

После выполнения:

- ✅ Полнофункциональный dashboard с реальными данными из Mock API
- ✅ 4 KPI-карты с метриками и трендами (на русском)
- ✅ Интерактивный график timeline
- ✅ Переключатель периодов (день/неделя/месяц)
- ✅ Автообновление каждые 30 секунд
- ✅ Responsive дизайн
- ✅ Loading и error states
- ✅ 100% TypeScript типизация
- ✅ Нулевых ошибок линтера

### To-dos

- [ ] Установить библиотеку Recharts для графиков
- [ ] Создать компонент PeriodSelector для выбора периода (День/Неделя/Месяц) на русском
- [ ] Создать компонент KPICard с маппингом меток на русский язык
- [ ] Создать компонент TimelineChart с Recharts и русскими метками
- [ ] Обновить главную страницу с интеграцией всех компонентов и API
- [ ] Добавить loading states, error handling и автообновление каждые 30 секунд
- [ ] Обеспечить responsive дизайн с Tailwind breakpoints (mobile-first)
- [ ] Протестировать dashboard с разными периодами, responsive и автообновлением
- [ ] Запустить make fe-check и исправить все ошибки линтера/TypeScript