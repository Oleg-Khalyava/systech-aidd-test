/**
 * PeriodSelector - переключатель периода статистики
 * Позволяет выбрать период: День, Неделя, Месяц
 */

import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import type { Period } from '@/types';

interface PeriodSelectorProps {
  value: Period;
  onChange: (period: Period) => void;
}

const PERIOD_LABELS: Record<Period, string> = {
  day: 'День',
  week: 'Неделя',
  month: 'Месяц',
};

export function PeriodSelector({ value, onChange }: PeriodSelectorProps) {
  return (
    <Tabs value={value} onValueChange={(v) => onChange(v as Period)}>
      <TabsList>
        <TabsTrigger value="day">{PERIOD_LABELS.day}</TabsTrigger>
        <TabsTrigger value="week">{PERIOD_LABELS.week}</TabsTrigger>
        <TabsTrigger value="month">{PERIOD_LABELS.month}</TabsTrigger>
      </TabsList>
    </Tabs>
  );
}
