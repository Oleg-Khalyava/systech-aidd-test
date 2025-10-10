"""Класс для работы с LLM через OpenRouter API"""

from openai import AsyncOpenAI


class LLMClient:
    """Клиент для работы с LLM
    
    Attributes:
        client: Асинхронный клиент OpenAI
        model: Название модели для использования
    """
    
    def __init__(self, api_key: str, base_url: str, model: str):
        """Инициализация клиента
        
        Args:
            api_key: API ключ для OpenRouter
            base_url: Базовый URL для OpenRouter API
            model: Название модели (например, openai/gpt-3.5-turbo)
        """
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url
        )
        self.model = model
    
    async def send_message(self, messages: list[dict]) -> str:
        """Отправка сообщения в LLM
        
        Args:
            messages: История сообщений в формате OpenAI
            
        Returns:
            str: Ответ от LLM
            
        Raises:
            Exception: При ошибках API
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"LLM API error: {e}")

