"""Middleware для Dependency Injection"""

import logging
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from src.dependencies import BotDependencies

logger = logging.getLogger("telegram_bot")


class DependencyInjectionMiddleware(BaseMiddleware):
    """Middleware для внедрения зависимостей в handlers

    Добавляет объект BotDependencies в data словарь каждого handler'а,
    устраняя необходимость в глобальных переменных.

    Attributes:
        dependencies: Контейнер с зависимостями бота
    """

    def __init__(self, dependencies: BotDependencies):
        """Инициализация middleware

        Args:
            dependencies: Контейнер с зависимостями бота
        """
        super().__init__()
        self.dependencies = dependencies

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """Обработка события с внедрением зависимостей

        Args:
            handler: Следующий обработчик в цепочке
            event: Событие от Telegram (Message, CallbackQuery и т.д.)
            data: Дополнительные данные

        Returns:
            Результат выполнения следующего обработчика
        """
        # Внедряем зависимости в data
        data["deps"] = self.dependencies

        # Передаем управление следующему обработчику
        return await handler(event, data)


