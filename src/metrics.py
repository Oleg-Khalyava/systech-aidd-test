"""Система метрик для мониторинга бота"""

import time
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class BotMetrics:
    """Класс для отслеживания метрик бота

    Attributes:
        total_requests: Общее количество запросов
        total_errors: Общее количество ошибок
        total_tokens: Общее количество использованных токенов
        total_cost: Примерная стоимость в долларах (токены * 0.00001)
        active_users: Множество активных пользователей
        start_time: Время запуска бота
    """

    total_requests: int = 0
    total_errors: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0
    active_users: set[int] = field(default_factory=set)
    start_time: float = field(default_factory=time.time)

    def increment_requests(self) -> None:
        """Увеличить счетчик запросов"""
        self.total_requests += 1

    def increment_errors(self) -> None:
        """Увеличить счетчик ошибок"""
        self.total_errors += 1

    def add_tokens(self, tokens: int, cost_per_token: float = 0.00001) -> None:
        """Добавить использованные токены

        Args:
            tokens: Количество токенов
            cost_per_token: Стоимость за токен (по умолчанию $0.00001)
        """
        self.total_tokens += tokens
        self.total_cost += tokens * cost_per_token

    def add_active_user(self, user_id: int) -> None:
        """Добавить активного пользователя

        Args:
            user_id: ID пользователя
        """
        self.active_users.add(user_id)

    def get_uptime(self) -> float:
        """Получить время работы бота в секундах

        Returns:
            float: Время работы в секундах
        """
        return time.time() - self.start_time

    def get_uptime_formatted(self) -> str:
        """Получить форматированное время работы

        Returns:
            str: Время работы в формате "Xд Xч Xм Xс"
        """
        uptime = int(self.get_uptime())
        days = uptime // 86400
        hours = (uptime % 86400) // 3600
        minutes = (uptime % 3600) // 60
        seconds = uptime % 60

        parts = []
        if days > 0:
            parts.append(f"{days}д")
        if hours > 0:
            parts.append(f"{hours}ч")
        if minutes > 0:
            parts.append(f"{minutes}м")
        parts.append(f"{seconds}с")

        return " ".join(parts)

    def get_error_rate(self) -> float:
        """Получить процент ошибок

        Returns:
            float: Процент ошибок от общего числа запросов
        """
        if self.total_requests == 0:
            return 0.0
        return (self.total_errors / self.total_requests) * 100

    def get_stats(self) -> dict[str, object]:
        """Получить все статистики в виде словаря

        Returns:
            dict: Словарь с метриками
        """
        return {
            "total_requests": self.total_requests,
            "total_errors": self.total_errors,
            "error_rate": f"{self.get_error_rate():.2f}%",
            "total_tokens": self.total_tokens,
            "total_cost": f"${self.total_cost:.4f}",
            "active_users": len(self.active_users),
            "uptime": self.get_uptime_formatted(),
            "start_time": datetime.fromtimestamp(self.start_time).strftime("%Y-%m-%d %H:%M:%S"),
        }

    def get_stats_formatted(self) -> str:
        """Получить форматированную строку со статистикой

        Returns:
            str: Форматированная статистика для отображения
        """
        stats = self.get_stats()
        lines = [
            "📊 **Статистика бота**",
            "",
            f"🔢 Всего запросов: {stats['total_requests']}",
            f"❌ Ошибок: {stats['total_errors']} ({stats['error_rate']})",
            f"👥 Активных пользователей: {stats['active_users']}",
            f"🪙 Использовано токенов: {stats['total_tokens']}",
            f"💰 Примерная стоимость: {stats['total_cost']}",
            f"⏱ Время работы: {stats['uptime']}",
            f"🚀 Запущен: {stats['start_time']}",
        ]
        return "\n".join(lines)

    def reset(self) -> None:
        """Сбросить все метрики (кроме времени запуска)"""
        self.total_requests = 0
        self.total_errors = 0
        self.total_tokens = 0
        self.total_cost = 0.0
        self.active_users = set()


