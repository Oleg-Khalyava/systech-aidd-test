"""Dependency Injection контейнер для зависимостей бота"""

from dataclasses import dataclass

from src.config import Config
from src.database import MessageRepository, UserRepository
from src.protocols import ILLMClient, IRoleManager


@dataclass
class BotDependencies:
    """Контейнер для всех зависимостей бота

    Инкапсулирует все зависимости в одном месте для удобной передачи
    через middleware и использования в handlers.

    Attributes:
        user_repo: Repository для работы с пользователями
        message_repo: Repository для работы с сообщениями
        llm_client: Клиент для работы с LLM
        role_manager: Менеджер ролей и системных промптов
        config: Конфигурация бота
    """

    user_repo: UserRepository
    message_repo: MessageRepository
    llm_client: ILLMClient
    role_manager: IRoleManager
    config: Config
