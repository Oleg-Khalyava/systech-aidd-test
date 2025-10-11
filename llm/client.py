"""Класс для работы с LLM через OpenRouter API"""

import logging

from openai import AsyncOpenAI

logger = logging.getLogger("telegram_bot")


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

    async def send_message(self, messages: list[dict[str, str]]) -> str:
        """Отправка сообщения в LLM

        Args:
            messages: История сообщений в формате OpenAI

        Returns:
            str: Ответ от LLM

        Raises:
            Exception: При ошибках API
        """
        logger.info(f"Sending request to LLM (model: {self.model}, messages count: {len(messages)})")

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages  # type: ignore[arg-type]
            )
            response_text = response.choices[0].message.content
            if response_text is None:
                raise Exception("LLM returned empty response")
            logger.info(
                f"Received response from LLM (length: {len(response_text)} chars, "
                f"tokens used: {response.usage.total_tokens if response.usage else 'N/A'})"
            )
            return response_text
        except Exception as e:
            logger.error(f"LLM API error: {e}", exc_info=True)
            # Не раскрываем детали ошибки API пользователю
            raise Exception("Failed to get response from LLM service")

