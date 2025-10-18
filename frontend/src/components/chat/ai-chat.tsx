'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Send, Settings, Trash2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { apiClient } from '@/lib/api';
import type { ChatMode, ChatMessage } from '@/types';

// Функция для получения или создания уникального user_id
function getUserId(): number {
    const storageKey = 'ai_chat_user_id';
    let userId = localStorage.getItem(storageKey);

    if (!userId) {
        // Генерируем уникальный ID на основе timestamp и случайного числа
        // Используем более надежную генерацию с большим диапазоном
        const timestamp = Date.now();
        const random = Math.floor(Math.random() * 999999);
        userId = String(timestamp + random);

        localStorage.setItem(storageKey, userId);
        console.log(`[AI Chat] Создан новый user ID: ${userId}`);
    } else {
        console.log(`[AI Chat] Загружен существующий user ID: ${userId}`);
    }

    return parseInt(userId, 10);
}

export default function AIChatCard({ className }: { className?: string }) {
    const [userId] = useState<number>(getUserId());
    const [messages, setMessages] = useState<ChatMessage[]>([
        {
            id: '1',
            role: 'assistant',
            content: '👋 Привет! Я ваш AI-ассистент. Выберите режим работы выше.',
            timestamp: new Date().toISOString(),
        },
    ]);
    const [input, setInput] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const [mode, setMode] = useState<ChatMode>('normal');
    const [showSql, setShowSql] = useState<string | null>(null);
    const [isLoadingHistory, setIsLoadingHistory] = useState(true);

    // Загрузить историю чата при монтировании
    useEffect(() => {
        const loadHistory = async () => {
            try {
                const history = await apiClient.getChatHistory(userId);

                if (history.messages.length > 0) {
                    // Преобразуем историю в формат ChatMessage
                    const historyMessages: ChatMessage[] = history.messages.map((msg) => ({
                        id: msg.id.toString(),
                        role: msg.role as 'user' | 'assistant',
                        content: msg.content,
                        timestamp: msg.created_at,
                    }));
                    setMessages(historyMessages);
                }
            } catch (error) {
                console.error('Failed to load chat history:', error);
                // В случае ошибки оставляем приветственное сообщение
            } finally {
                setIsLoadingHistory(false);
            }
        };

        loadHistory();
    }, [userId]);

    const handleSend = async () => {
        if (!input.trim()) return;

        // Добавляем сообщение пользователя
        const userMessage: ChatMessage = {
            id: Date.now().toString(),
            role: 'user',
            content: input,
            timestamp: new Date().toISOString(),
        };
        setMessages((prev) => [...prev, userMessage]);
        setInput('');
        setIsTyping(true);

        try {
            // Отправляем запрос к API
            const response = await apiClient.sendChatMessage(userId, input, mode);

            // Добавляем ответ AI
            const aiMessage: ChatMessage = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: response.message,
                timestamp: new Date().toISOString(),
                sql: response.sql,
            };
            setMessages((prev) => [...prev, aiMessage]);

            // Если есть SQL, можем показать его
            if (response.sql) {
                setShowSql(response.sql);
            }
        } catch (error) {
            // Показываем ошибку как сообщение
            const errorMessage: ChatMessage = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: `❌ Ошибка: ${error instanceof Error ? error.message : 'Неизвестная ошибка'}`,
                timestamp: new Date().toISOString(),
            };
            setMessages((prev) => [...prev, errorMessage]);
        } finally {
            setIsTyping(false);
        }
    };

    const toggleMode = () => {
        setMode((prev) => (prev === 'normal' ? 'admin' : 'normal'));
    };

    const clearHistory = () => {
        if (confirm('Очистить историю чата? Это действие необратимо.')) {
            setMessages([
                {
                    id: '1',
                    role: 'assistant',
                    content: '👋 История очищена! Начнем новый разговор.',
                    timestamp: new Date().toISOString(),
                },
            ]);
            console.log('[AI Chat] История чата очищена');
        }
    };

    return (
        <div
            className={cn(
                'relative w-[360px] h-[580px] rounded-2xl overflow-hidden p-[2px]',
                className
            )}
        >
            {/* Animated Outer Border */}
            <motion.div
                className="absolute inset-0 rounded-2xl border-2 border-white/20"
                animate={{ rotate: [0, 360] }}
                transition={{ duration: 25, repeat: Infinity, ease: 'linear' }}
            />

            {/* Inner Card */}
            <div className="relative flex flex-col w-full h-full rounded-xl border border-white/10 overflow-hidden bg-black/90 backdrop-blur-xl">
                {/* Inner Animated Background */}
                <motion.div
                    className="absolute inset-0 bg-gradient-to-br from-gray-800 via-black to-gray-900"
                    animate={{ backgroundPosition: ['0% 0%', '100% 100%', '0% 0%'] }}
                    transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
                    style={{ backgroundSize: '200% 200%' }}
                />

                {/* Floating Particles */}
                {Array.from({ length: 20 }).map((_, i) => (
                    <motion.div
                        key={i}
                        className="absolute w-1 h-1 rounded-full bg-white/10"
                        animate={{
                            y: ['0%', '-140%'],
                            x: [Math.random() * 200 - 100, Math.random() * 200 - 100],
                            opacity: [0, 1, 0],
                        }}
                        transition={{
                            duration: 5 + Math.random() * 3,
                            repeat: Infinity,
                            delay: i * 0.5,
                            ease: 'easeInOut',
                        }}
                        style={{ left: `${Math.random() * 100}%`, bottom: '-10%' }}
                    />
                ))}

                {/* Header */}
                <div className="px-4 py-3 border-b border-white/10 relative z-10 flex items-center justify-between">
                    <h2 className="text-lg font-semibold text-white">
                        🤖 AI Ассистент
                    </h2>
                    <div className="flex items-center gap-2">
                        <button
                            onClick={clearHistory}
                            className="p-2 rounded-lg bg-white/10 hover:bg-white/20 transition-colors text-white"
                            title="Очистить историю"
                        >
                            <Trash2 className="w-4 h-4" />
                        </button>
                        <button
                            onClick={toggleMode}
                            className="flex items-center gap-2 px-3 py-1 rounded-lg bg-white/10 hover:bg-white/20 transition-colors text-sm text-white"
                            title="Переключить режим"
                        >
                            <Settings className="w-4 h-4" />
                            <span>{mode === 'normal' ? 'Обычный' : 'Администратор'}</span>
                        </button>
                    </div>
                </div>

                {/* Mode Indicator */}
                <div className="px-4 py-2 border-b border-white/10 relative z-10">
                    <p className="text-xs text-white/60">
                        {mode === 'normal'
                            ? '💬 Режим: Обычный чат с AI'
                            : '⚙️ Режим: Администратор (аналитика БД)'}
                    </p>
                    <p className="text-xs text-white/40 mt-1">
                        🆔 User ID: {userId}
                    </p>
                </div>

                {/* Messages */}
                <div className="flex-1 px-4 py-3 overflow-y-auto space-y-3 text-sm flex flex-col relative z-10">
                    {isLoadingHistory ? (
                        <div className="flex items-center justify-center h-full">
                            <span className="text-white/50">Загрузка истории...</span>
                        </div>
                    ) : (
                        messages.map((msg) => (
                            <motion.div
                                key={msg.id}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ duration: 0.4 }}
                                className={cn(
                                    'px-3 py-2 rounded-xl max-w-[80%] shadow-md backdrop-blur-md',
                                    msg.role === 'assistant'
                                        ? 'bg-white/10 text-white self-start'
                                        : 'bg-white/30 text-black font-semibold self-end'
                                )}
                            >
                                <div className="whitespace-pre-wrap break-words">{msg.content}</div>
                                {msg.sql && (
                                    <details className="mt-2 text-xs">
                                        <summary className="cursor-pointer text-white/70 hover:text-white">
                                            SQL запрос
                                        </summary>
                                        <pre className="mt-1 p-2 bg-black/30 rounded text-green-400 overflow-x-auto">
                                            {msg.sql}
                                        </pre>
                                    </details>
                                )}
                            </motion.div>
                        ))
                    )}

                    {/* AI Typing Indicator */}
                    {isTyping && (
                        <motion.div
                            className="flex items-center gap-1 px-3 py-2 rounded-xl max-w-[30%] bg-white/10 self-start"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: [0, 1, 0.6, 1] }}
                            transition={{ repeat: Infinity, duration: 1.2 }}
                        >
                            <span className="w-2 h-2 rounded-full bg-white animate-pulse"></span>
                            <span className="w-2 h-2 rounded-full bg-white animate-pulse delay-200"></span>
                            <span className="w-2 h-2 rounded-full bg-white animate-pulse delay-400"></span>
                        </motion.div>
                    )}
                </div>

                {/* Input */}
                <div className="flex items-center gap-2 p-3 border-t border-white/10 relative z-10">
                    <input
                        className="flex-1 px-3 py-2 text-sm bg-black/50 rounded-lg border border-white/10 text-white placeholder-white/50 focus:outline-none focus:ring-1 focus:ring-white/50"
                        placeholder="Введите сообщение..."
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                        disabled={isTyping}
                    />
                    <button
                        onClick={handleSend}
                        disabled={isTyping || !input.trim()}
                        className="p-2 rounded-lg bg-white/10 hover:bg-white/20 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        <Send className="w-4 h-4 text-white" />
                    </button>
                </div>
            </div>
        </div>
    );
}

