"""Тесты для Dependency Injection"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from aiogram.types import Chat, Message, User

from src.config import Config
from src.conversation import ConversationStorage
from src.dependencies import BotDependencies
from src.middlewares.dependency_injection import DependencyInjectionMiddleware
from src.user import UserStorage


@pytest.fixture
def mock_user_storage() -> UserStorage:
    """Создает хранилище пользователей"""
    return UserStorage()


@pytest.fixture
def mock_conversation_storage() -> ConversationStorage:
    """Создает хранилище диалогов"""
    return ConversationStorage()


@pytest.fixture
def mock_llm_client() -> AsyncMock:
    """Создает мок LLM клиента"""
    return AsyncMock()


@pytest.fixture
def mock_role_manager() -> MagicMock:
    """Создает мок менеджера ролей"""
    role_manager = MagicMock()
    role_manager.get_system_prompt.return_value = "You are helpful"
    role_manager.get_role_description.return_value = "AI Assistant"
    return role_manager


@pytest.fixture
def mock_config() -> Config:
    """Создает мок конфигурации"""
    config = MagicMock(spec=Config)
    config.welcome_message = "Welcome!"
    config.default_system_prompt = "You are helpful"
    config.max_context_messages = 10
    return config


@pytest.fixture
def dependencies(
    mock_user_storage: UserStorage,
    mock_conversation_storage: ConversationStorage,
    mock_llm_client: AsyncMock,
    mock_role_manager: MagicMock,
    mock_config: Config,
) -> BotDependencies:
    """Создает контейнер зависимостей"""
    return BotDependencies(
        user_storage=mock_user_storage,
        conversation_storage=mock_conversation_storage,
        llm_client=mock_llm_client,
        role_manager=mock_role_manager,
        config=mock_config,
    )


def test_bot_dependencies_creation(dependencies: BotDependencies) -> None:
    """Тест создания контейнера зависимостей"""
    assert dependencies.user_storage is not None
    assert dependencies.conversation_storage is not None
    assert dependencies.llm_client is not None
    assert dependencies.role_manager is not None
    assert dependencies.config is not None


def test_bot_dependencies_user_storage(dependencies: BotDependencies) -> None:
    """Тест доступа к user_storage через dependencies"""
    # Создаем пользователя
    user = dependencies.user_storage.get_or_create(
        chat_id=123, username="test", first_name="Test", default_role="role"
    )

    # Проверяем что он сохранен
    retrieved_user = dependencies.user_storage.get(123)
    assert retrieved_user is user


def test_bot_dependencies_conversation_storage(dependencies: BotDependencies) -> None:
    """Тест доступа к conversation_storage через dependencies"""
    # Создаем диалог
    conversation = dependencies.conversation_storage.get_or_create(123)

    # Проверяем что он сохранен
    retrieved_conversation = dependencies.conversation_storage.get(123)
    assert retrieved_conversation is conversation


def test_bot_dependencies_config_access(dependencies: BotDependencies) -> None:
    """Тест доступа к конфигурации через dependencies"""
    assert dependencies.config.welcome_message == "Welcome!"
    assert dependencies.config.default_system_prompt == "You are helpful"
    assert dependencies.config.max_context_messages == 10


@pytest.fixture
def mock_handler() -> AsyncMock:
    """Создает мок handler'а"""
    return AsyncMock(return_value=None)


@pytest.fixture
def mock_message() -> Message:
    """Создает мок сообщения"""
    message = MagicMock(spec=Message)
    message.from_user = User(id=123, is_bot=False, first_name="Test")
    message.chat = Chat(id=123, type="private")
    return message


@pytest.mark.asyncio
async def test_dependency_injection_middleware_injects_dependencies(
    dependencies: BotDependencies, mock_handler: AsyncMock, mock_message: Message
) -> None:
    """Тест что middleware добавляет dependencies в data"""
    middleware = DependencyInjectionMiddleware(dependencies)
    data: dict[str, object] = {}

    # Вызываем middleware
    await middleware(mock_handler, mock_message, data)

    # Проверяем что dependencies добавлен в data
    assert "deps" in data
    assert data["deps"] is dependencies

    # Проверяем что handler был вызван с правильными параметрами
    mock_handler.assert_called_once_with(mock_message, data)


@pytest.mark.asyncio
async def test_dependency_injection_middleware_passes_through(
    dependencies: BotDependencies, mock_handler: AsyncMock, mock_message: Message
) -> None:
    """Тест что middleware пропускает событие дальше"""
    middleware = DependencyInjectionMiddleware(dependencies)
    data: dict[str, object] = {"existing_key": "existing_value"}

    # Вызываем middleware
    await middleware(mock_handler, mock_message, data)

    # Проверяем что существующие данные сохранены
    assert data["existing_key"] == "existing_value"

    # Проверяем что handler был вызван
    mock_handler.assert_called_once()


@pytest.mark.asyncio
async def test_dependency_injection_middleware_immutable_dependencies(
    dependencies: BotDependencies, mock_handler: AsyncMock, mock_message: Message
) -> None:
    """Тест что dependencies одни и те же при нескольких вызовах"""
    middleware = DependencyInjectionMiddleware(dependencies)

    # Первый вызов
    data1: dict[str, object] = {}
    await middleware(mock_handler, mock_message, data1)

    # Второй вызов
    data2: dict[str, object] = {}
    await middleware(mock_handler, mock_message, data2)

    # Проверяем что это один и тот же объект dependencies
    assert data1["deps"] is data2["deps"]
    assert data1["deps"] is dependencies
