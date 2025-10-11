"""Валидаторы для проверки входящих данных"""

import logging

logger = logging.getLogger("telegram_bot")

# Константы для валидации
MAX_MESSAGE_LENGTH = 4000


class MessageValidator:
    """Валидатор для проверки текстовых сообщений от пользователей

    Attributes:
        max_length: Максимальная длина сообщения
    """

    def __init__(self, max_length: int = MAX_MESSAGE_LENGTH):
        """Инициализация валидатора

        Args:
            max_length: Максимальная длина сообщения (по умолчанию 4000 символов)
        """
        self.max_length = max_length

    def validate(self, text: str | None) -> tuple[bool, str | None]:
        """Проверка валидности текстового сообщения

        Args:
            text: Текст сообщения для проверки

        Returns:
            Кортеж (валидно, сообщение об ошибке).
            Если сообщение валидно, возвращается (True, None).
            Если не валидно, возвращается (False, текст ошибки для пользователя).
        """
        # Проверка на None
        if text is None:
            return False, "❌ Пожалуйста, отправьте текстовое сообщение."

        # Проверка на пустое сообщение (только пробелы)
        if not text.strip():
            logger.warning("Received empty message (only whitespace)")
            return False, "❌ Сообщение не может быть пустым. Пожалуйста, введите текст."

        # Проверка длины сообщения
        if len(text) > self.max_length:
            logger.warning(f"Received too long message: {len(text)} chars (max: {self.max_length})")
            return False, (
                f"❌ Ваше сообщение слишком длинное ({len(text)} символов). "
                f"Максимальная длина: {self.max_length} символов. "
                f"Пожалуйста, разбейте его на несколько сообщений."
            )

        # Сообщение валидно
        return True, None


