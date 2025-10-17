/**
 * TimelineChart - график активности (timeline)
 * Отображает временной ряд с количеством сообщений
 */

'use client';

import { useTheme } from 'next-themes';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import type { TimelinePoint } from '@/types';
import {
    Area,
    AreaChart,
    CartesianGrid,
    ResponsiveContainer,
    Tooltip,
    XAxis,
    YAxis,
} from 'recharts';

interface TimelineChartProps {
    data: TimelinePoint[];
    loading?: boolean;
}

export function TimelineChart({ data, loading }: TimelineChartProps) {
    const { theme } = useTheme();
    const isDark = theme === 'dark';

    // Цвета для графика в зависимости от темы
    // В темной теме используем зеленый "матричный" цвет (#00ff41)
    const chartColors = {
        stroke: isDark ? '#00ff41' : 'hsl(var(--primary))',
        fill: isDark ? 'url(#colorMatrixGreen)' : 'url(#colorValueLight)',
    };

    // Форматирование даты для оси X
    const formatDate = (dateStr: string) => {
        const date = new Date(dateStr);
        return date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' });
    };

    // Кастомный Tooltip
    const CustomTooltip = ({
        active,
        payload,
    }: {
        active?: boolean;
        payload?: Array<{ payload: TimelinePoint }>;
    }) => {
        if (active && payload && payload.length) {
            const data = payload[0].payload;
            return (
                <div className="bg-card border border-border rounded-lg shadow-lg p-3">
                    <p className="text-sm font-medium">
                        {new Date(data.date).toLocaleDateString('ru-RU', {
                            day: 'numeric',
                            month: 'long',
                            year: 'numeric',
                        })}
                    </p>
                    <p className="text-sm text-muted-foreground mt-1">
                        Сообщений: <span className="font-bold text-foreground">{data.value}</span>
                    </p>
                </div>
            );
        }
        return null;
    };

    if (loading) {
        return (
            <Card className="dark:bg-gray-800/60 dark:border-gray-700">
                <CardHeader>
                    <CardTitle>График активности</CardTitle>
                    <CardDescription>Загрузка данных...</CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="h-[300px] flex items-center justify-center">
                        <div className="animate-pulse text-muted-foreground">Загрузка...</div>
                    </div>
                </CardContent>
            </Card>
        );
    }

    if (!data || data.length === 0) {
        return (
            <Card className="dark:bg-gray-800/60 dark:border-gray-700">
                <CardHeader>
                    <CardTitle>График активности</CardTitle>
                    <CardDescription>Данные временного ряда</CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="h-[300px] flex items-center justify-center">
                        <p className="text-muted-foreground">Нет данных для отображения</p>
                    </div>
                </CardContent>
            </Card>
        );
    }

    return (
        <Card className="dark:bg-gray-800/60 dark:border-gray-700">
            <CardHeader>
                <CardTitle>График активности</CardTitle>
                <CardDescription>Количество сообщений за выбранный период</CardDescription>
            </CardHeader>
            <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                    <AreaChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                        <defs>
                            {/* Градиент для светлой темы */}
                            <linearGradient id="colorValueLight" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="hsl(var(--primary))" stopOpacity={0.4} />
                                <stop offset="95%" stopColor="hsl(var(--primary))" stopOpacity={0.05} />
                            </linearGradient>
                            {/* Градиент для темной темы - зеленый "матричный" стиль */}
                            <linearGradient id="colorMatrixGreen" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="0%" stopColor="#00ff41" stopOpacity={0.8} />
                                <stop offset="50%" stopColor="#00ff41" stopOpacity={0.4} />
                                <stop offset="100%" stopColor="#00ff41" stopOpacity={0.1} />
                            </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" className="stroke-muted" opacity={0.3} />
                        <XAxis
                            dataKey="date"
                            tickFormatter={formatDate}
                            className="text-xs"
                            stroke="hsl(var(--muted-foreground))"
                        />
                        <YAxis className="text-xs" stroke="hsl(var(--muted-foreground))" />
                        <Tooltip content={<CustomTooltip />} />
                        <Area
                            type="monotone"
                            dataKey="value"
                            stroke={chartColors.stroke}
                            strokeWidth={isDark ? 2 : 3}
                            fillOpacity={1}
                            fill={chartColors.fill}
                        />
                    </AreaChart>
                </ResponsiveContainer>
            </CardContent>
        </Card>
    );
}
