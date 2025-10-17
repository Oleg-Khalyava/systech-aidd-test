/**
 * Dashboard Page
 * Главная страница с дашбордом статистики Telegram бота
 */

'use client';

import { useCallback, useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { getStats } from '@/lib/api';
import type { StatsResponse, Period } from '@/types';
import { PeriodSelector } from '@/components/dashboard/period-selector';
import { KPICard } from '@/components/dashboard/kpi-card';
import { TimelineChart } from '@/components/dashboard/timeline-chart';
import { FloatingChatButton } from '@/components/chat/floating-chat-button';

export default function DashboardPage() {
  const [period, setPeriod] = useState<Period>('week');
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Функция загрузки данных
  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getStats(period);
      setStats(data);
    } catch (err) {
      console.error('Failed to fetch stats:', err);
      setError(
        err instanceof Error ? err.message : 'Ошибка загрузки данных. Проверьте, что API запущен.'
      );
    } finally {
      setLoading(false);
    }
  }, [period]);

  // Загрузка данных при изменении периода
  useEffect(() => {
    fetchData();
    // Автообновление каждые 30 секунд
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, [fetchData]);

  return (
    <>
      <div className="space-y-6">
        {/* Заголовок и переключатель периода */}
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-3xl font-bold">Дашборд</h1>
            <p className="text-muted-foreground">Статистика Telegram бота</p>
          </div>
          <PeriodSelector value={period} onChange={setPeriod} />
        </div>

        {/* Error state */}
        {error && (
          <Card className="border-destructive">
            <CardHeader>
              <CardTitle className="text-destructive">Ошибка загрузки</CardTitle>
              <CardDescription>{error}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                <Button onClick={fetchData} variant="outline" size="sm">
                  Повторить попытку
                </Button>
                <span className="text-sm text-muted-foreground">
                  Команда: <code className="bg-muted px-2 py-1 rounded">make api-run</code>
                </span>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Loading skeleton для KPI карт */}
        {loading && !stats && (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {[1, 2, 3, 4].map((i) => (
              <Card key={i}>
                <CardHeader className="pb-2">
                  <div className="h-4 bg-muted rounded animate-pulse w-2/3" />
                  <div className="h-8 bg-muted rounded animate-pulse w-1/2 mt-2" />
                </CardHeader>
                <CardContent>
                  <div className="h-4 bg-muted rounded animate-pulse w-1/3" />
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* KPI Metrics Grid */}
        {stats && (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {stats.kpi_metrics.map((metric) => (
              <KPICard key={metric.label} {...metric} />
            ))}
          </div>
        )}

        {/* Timeline Chart */}
        <TimelineChart data={stats?.timeline || []} loading={loading && !stats} />

        {/* Auto-refresh indicator */}
        {stats && !loading && (
          <div className="flex items-center justify-center">
            <Badge variant="outline" className="text-xs">
              ✓ Автообновление каждые 30 секунд
            </Badge>
          </div>
        )}
      </div>

      {/* Floating Chat Button */}
      <FloatingChatButton />
    </>
  );
}
