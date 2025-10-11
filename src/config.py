"""Класс конфигурации для загрузки настроек из .env файла"""

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass
class Config:
    """Конфигурация бота

    Attributes:
        telegram_bot_token: Токен Telegram бота
        openrouter_api_key: API ключ OpenRouter
        openrouter_base_url: Базовый URL OpenRouter API
        openrouter_model: Модель LLM для использования
        default_system_prompt: Системный промпт по умолчанию
        max_context_messages: Максимальное количество сообщений в контексте
        welcome_message: Текст приветственного сообщения
        max_storage_size: Максимальное количество записей в storage (LRU)
        storage_ttl_hours: Время жизни записей в storage (в часах)
    """

    telegram_bot_token: str
    openrouter_api_key: str
    openrouter_base_url: str
    openrouter_model: str
    default_system_prompt: str
    max_context_messages: int
    welcome_message: str
    max_storage_size: int
    storage_ttl_hours: int

    @classmethod
    def load(cls) -> "Config":
        """Загрузка конфигурации из .env файла

        Returns:
            Config: Объект конфигурации

        Raises:
            ValueError: Если обязательные параметры не указаны или имеют неверный формат
        """
        load_dotenv()

        # Обязательные параметры
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not token:
            raise ValueError("TELEGRAM_BOT_TOKEN is required in .env file")
        if not token.strip():
            raise ValueError("TELEGRAM_BOT_TOKEN cannot be empty")

        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY is required in .env file")
        if not api_key.strip():
            raise ValueError("OPENROUTER_API_KEY cannot be empty")

        # Параметры с значениями по умолчанию
        base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        model = os.getenv("OPENROUTER_MODEL", "gpt-oss-20b")
        system_prompt = os.getenv(
            "DEFAULT_SYSTEM_PROMPT", "Ты полезный AI-ассистент"
        )

        # Валидация числовых параметров
        max_messages_str = os.getenv("MAX_CONTEXT_MESSAGES", "10")
        try:
            max_messages = int(max_messages_str)
            if max_messages <= 0:
                raise ValueError("MAX_CONTEXT_MESSAGES must be greater than 0")
        except ValueError as e:
            if "invalid literal" in str(e):
                raise ValueError(f"MAX_CONTEXT_MESSAGES must be a valid integer, got: {max_messages_str}")
            raise

        welcome_msg = os.getenv(
            "WELCOME_MESSAGE",
            "я AI-ассистент на базе LLM. Задавай любые вопросы, и я постараюсь помочь!"
        )

        # Параметры для управления памятью
        max_storage_str = os.getenv("MAX_STORAGE_SIZE", "1000")
        try:
            max_storage = int(max_storage_str)
            if max_storage <= 0:
                raise ValueError("MAX_STORAGE_SIZE must be greater than 0")
        except ValueError as e:
            if "invalid literal" in str(e):
                raise ValueError(f"MAX_STORAGE_SIZE must be a valid integer, got: {max_storage_str}")
            raise

        storage_ttl_str = os.getenv("STORAGE_TTL_HOURS", "24")
        try:
            storage_ttl = int(storage_ttl_str)
            if storage_ttl <= 0:
                raise ValueError("STORAGE_TTL_HOURS must be greater than 0")
        except ValueError as e:
            if "invalid literal" in str(e):
                raise ValueError(f"STORAGE_TTL_HOURS must be a valid integer, got: {storage_ttl_str}")
            raise

        return cls(
            telegram_bot_token=token.strip(),
            openrouter_api_key=api_key.strip(),
            openrouter_base_url=base_url,
            openrouter_model=model,
            default_system_prompt=system_prompt,
            max_context_messages=max_messages,
            welcome_message=welcome_msg,
            max_storage_size=max_storage,
            storage_ttl_hours=storage_ttl,
        )

