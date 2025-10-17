/**
 * KPICard - карта KPI-метрики
 * Отображает метрику со значением, трендом и процентом изменения
 */

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import type { KPIMetric } from '@/types';

type KPICardProps = KPIMetric;

// Маппинг английских меток на русские
const LABEL_MAPPING: Record<string, string> = {
  'Total Users': 'Всего пользователей',
  'Total Messages': 'Всего сообщений',
  'Deleted Messages': 'Удаленные сообщения',
  'Avg Message Length': 'Средняя длина сообщения',
};

// Иконки трендов
const TREND_ICONS = {
  up: '↑',
  down: '↓',
  stable: '→',
} as const;

export function KPICard({ label, value, change, trend }: KPICardProps) {
  // Переводим метку на русский, если есть маппинг
  const russianLabel = LABEL_MAPPING[label] || label;

  // Определяем цвет на основе тренда
  const trendColor =
    trend === 'up'
      ? 'text-green-600 dark:text-green-400'
      : trend === 'down'
        ? 'text-red-600 dark:text-red-400'
        : 'text-gray-600 dark:text-gray-400';

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardDescription>{russianLabel}</CardDescription>
        <CardTitle className="text-3xl font-bold">{value}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className={`flex items-center gap-1 text-sm font-medium ${trendColor}`}>
          <span>{TREND_ICONS[trend]}</span>
          <span>
            {change > 0 ? '+' : ''}
            {change.toFixed(1)}%
          </span>
        </div>
        <p className="text-xs text-muted-foreground mt-1">
          {trend === 'up'
            ? 'Рост за период'
            : trend === 'down'
              ? 'Снижение за период'
              : 'Без изменений'}
        </p>
      </CardContent>
    </Card>
  );
}
