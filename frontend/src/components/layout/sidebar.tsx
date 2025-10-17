/**
 * Sidebar компонент
 * Боковое навигационное меню
 */

'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';

const navigation = [
    { name: 'Dashboard', href: '/', icon: '📊' },
    { name: 'AI Chat', href: '/chat', icon: '💬', disabled: true },
];

export function Sidebar() {
    const pathname = usePathname();

    return (
        <aside className="w-64 border-r bg-gray-50">
            <div className="flex h-16 items-center border-b px-6">
                <span className="text-lg font-semibold">Navigation</span>
            </div>
            <nav className="space-y-1 p-4">
                {navigation.map((item) => {
                    const isActive = pathname === item.href;
                    return (
                        <Link
                            key={item.name}
                            href={item.disabled ? '#' : item.href}
                            className={cn(
                                'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                                isActive
                                    ? 'bg-gray-900 text-white'
                                    : 'text-gray-700 hover:bg-gray-200',
                                item.disabled && 'cursor-not-allowed opacity-50'
                            )}
                            aria-disabled={item.disabled}
                        >
                            <span className="text-lg">{item.icon}</span>
                            {item.name}
                            {item.disabled && (
                                <span className="ml-auto text-xs text-gray-500">(SP-FE-4)</span>
                            )}
                        </Link>
                    );
                })}
            </nav>
        </aside>
    );
}

