/**
 * Dashboard Page
 * Главная страница с placeholder для дашборда статистики
 */

'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { healthCheck } from '@/lib/api';

export default function DashboardPage() {
  const [apiStatus, setApiStatus] = useState<'checking' | 'online' | 'offline'>('checking');

  useEffect(() => {
    // Проверка подключения к API
    healthCheck()
      .then(() => setApiStatus('online'))
      .catch(() => setApiStatus('offline'));
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="text-gray-600">Статистика Telegram бота</p>
      </div>

      {/* API Status */}
      <Card>
        <CardHeader>
          <CardTitle>Статус Backend API</CardTitle>
          <CardDescription>Проверка подключения к http://localhost:8000</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-2">
            {apiStatus === 'checking' && <Badge variant="secondary">Проверка...</Badge>}
            {apiStatus === 'online' && (
              <>
                <Badge className="bg-green-500">✓ Онлайн</Badge>
                <span className="text-sm text-gray-600">API готов к работе</span>
              </>
            )}
            {apiStatus === 'offline' && (
              <>
                <Badge variant="destructive">✗ Офлайн</Badge>
                <span className="text-sm text-gray-600">
                  Запустите API: <code className="bg-gray-100 px-2 py-1 rounded">make api-run</code>
                </span>
              </>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Placeholder для Dashboard */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {['Total Users', 'Total Messages', 'Deleted Messages', 'Avg Message Length'].map(
          (metric) => (
            <Card key={metric}>
              <CardHeader className="pb-2">
                <CardDescription>{metric}</CardDescription>
                <CardTitle className="text-3xl">-</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-xs text-gray-600">SP-FE-3: Реализация dashboard</p>
              </CardContent>
            </Card>
          )
        )}
      </div>

      {/* Info Card */}
      <Card>
        <CardHeader>
          <CardTitle>🚀 SP-FE-2 Завершен!</CardTitle>
          <CardDescription>Frontend каркас проекта готов</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 text-sm">
            <p>✅ Next.js 14+ с App Router</p>
            <p>✅ TypeScript strict mode</p>
            <p>✅ shadcn/ui компоненты установлены</p>
            <p>✅ Tailwind CSS настроен</p>
            <p>✅ API клиент с типами создан</p>
            <p>✅ Layout компоненты готовы</p>
            <p className="pt-2 font-medium">
              Следующий спринт: SP-FE-3 - Реализация dashboard
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
