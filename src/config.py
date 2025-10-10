"""Класс конфигурации для загрузки настроек из .env файла"""

from dataclasses import dataclass
from dotenv import load_dotenv
import os


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
    """
    
    telegram_bot_token: str
    openrouter_api_key: str
    openrouter_base_url: str
    openrouter_model: str
    default_system_prompt: str
    max_context_messages: int
    
    @classmethod
    def load(cls) -> "Config":
        """Загрузка конфигурации из .env файла
        
        Returns:
            Config: Объект конфигурации
            
        Raises:
            ValueError: Если обязательные параметры не указаны
        """
        load_dotenv()
        
        # Обязательные параметры
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not token:
            raise ValueError("TELEGRAM_BOT_TOKEN is required in .env file")
        
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY is required in .env file")
        
        # Параметры с значениями по умолчанию
        base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        model = os.getenv("OPENROUTER_MODEL", "gpt-oss-20b")
        system_prompt = os.getenv(
            "DEFAULT_SYSTEM_PROMPT", "Ты полезный AI-ассистент"
        )
        max_messages = int(os.getenv("MAX_CONTEXT_MESSAGES", "10"))
        
        return cls(
            telegram_bot_token=token,
            openrouter_api_key=api_key,
            openrouter_base_url=base_url,
            openrouter_model=model,
            default_system_prompt=system_prompt,
            max_context_messages=max_messages,
        )

