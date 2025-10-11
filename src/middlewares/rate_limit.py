"""Middleware для ограничения частоты запросов (Rate Limiting)"""

import logging
import time
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

logger = logging.getLogger("telegram_bot")


class RateLimitMiddleware(BaseMiddleware):
    """Middleware для ограничения частоты запросов от пользователей

    Ограничивает количество сообщений от каждого пользователя до одного
    сообщения в указанный интервал времени.

    Attributes:
        rate_limit: Минимальный интервал между сообщениями в секундах
        user_last_message: Словарь для хранения времени последнего сообщения каждого пользователя
    """

    def __init__(self, rate_limit: float = 2.0):
        """Инициализация middleware

        Args:
            rate_limit: Минимальный интервал между сообщениями в секундах (по умолчанию 2 секунды)
        """
        super().__init__()
        self.rate_limit = rate_limit
        self.user_last_message: dict[int, float] = {}

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """Обработка сообщения с проверкой rate limit

        Args:
            handler: Следующий обработчик в цепочке
            event: Событие от Telegram
            data: Дополнительные данные

        Returns:
            Результат выполнения следующего обработчика или None если rate limit превышен
        """
        # Проверяем что это Message и у него есть from_user
        if not isinstance(event, Message) or not event.from_user:
            return await handler(event, data)

        user_id = event.from_user.id
        current_time = time.time()

        # Проверяем время последнего сообщения от пользователя
        last_message_time = self.user_last_message.get(user_id, 0)
        time_passed = current_time - last_message_time

        if time_passed < self.rate_limit:
            # Rate limit превышен
            wait_time = int(self.rate_limit - time_passed) + 1
            logger.warning(
                f"Rate limit exceeded for user {user_id} "
                f"(@{event.from_user.username}). Time passed: {time_passed:.2f}s"
            )
            await event.answer(
                f"⏳ Пожалуйста, подождите {wait_time} сек. перед отправкой следующего сообщения."
            )
            return None

        # Обновляем время последнего сообщения
        self.user_last_message[user_id] = current_time

        # Пропускаем сообщение дальше
        return await handler(event, data)

