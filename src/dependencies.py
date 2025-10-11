"""Dependency Injection контейнер для зависимостей бота"""

from dataclasses import dataclass

from src.config import Config
from src.protocols import IConversationStorage, ILLMClient, IRoleManager, IUserStorage


@dataclass
class BotDependencies:
    """Контейнер для всех зависимостей бота

    Инкапсулирует все зависимости в одном месте для удобной передачи
    через middleware и использования в handlers.

    Attributes:
        user_storage: Хранилище пользователей
        conversation_storage: Хранилище диалогов
        llm_client: Клиент для работы с LLM
        role_manager: Менеджер ролей и системных промптов
        config: Конфигурация бота
    """

    user_storage: IUserStorage
    conversation_storage: IConversationStorage
    llm_client: ILLMClient
    role_manager: IRoleManager
    config: Config
