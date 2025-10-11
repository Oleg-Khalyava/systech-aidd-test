"""Protocol интерфейсы для Dependency Inversion"""

from typing import Protocol

from src.conversation import Conversation
from src.user import User


class IUserStorage(Protocol):
    """Интерфейс для хранилища пользователей

    Определяет контракт для работы с пользователями.
    """

    def get_or_create(
        self, chat_id: int, username: str | None, first_name: str, default_role: str
    ) -> User:
        """Получить пользователя или создать нового

        Args:
            chat_id: ID чата
            username: Username пользователя
            first_name: Имя пользователя
            default_role: Роль по умолчанию

        Returns:
            User: Объект пользователя
        """
        ...

    def get(self, chat_id: int) -> User | None:
        """Получить пользователя по chat_id

        Args:
            chat_id: ID чата

        Returns:
            User | None: Объект пользователя или None
        """
        ...


class IConversationStorage(Protocol):
    """Интерфейс для хранилища диалогов

    Определяет контракт для работы с диалогами.
    """

    def get_or_create(self, chat_id: int) -> Conversation:
        """Получить диалог или создать новый

        Args:
            chat_id: ID чата

        Returns:
            Conversation: Объект диалога
        """
        ...

    def get(self, chat_id: int) -> Conversation | None:
        """Получить диалог по chat_id

        Args:
            chat_id: ID чата

        Returns:
            Conversation | None: Объект диалога или None
        """
        ...


class ILLMClient(Protocol):
    """Интерфейс для клиента LLM

    Определяет контракт для работы с LLM сервисом.
    """

    async def send_message(self, messages: list[dict[str, str]]) -> str:
        """Отправка сообщения в LLM

        Args:
            messages: История сообщений в формате OpenAI

        Returns:
            str: Ответ от LLM

        Raises:
            Exception: При ошибках API
        """
        ...

