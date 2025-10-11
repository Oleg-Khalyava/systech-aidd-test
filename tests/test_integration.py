"""Интеграционные тесты для полного flow обработки сообщений"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from aiogram.types import Chat, Message, User

from src.config import Config
from src.conversation import ConversationStorage
from src.dependencies import BotDependencies
from src.handlers.handlers import cmd_clear, cmd_start, message_handler
from src.user import UserStorage


@pytest.fixture
def mock_user() -> User:
    """Создает мок пользователя Telegram"""
    return User(id=123456, is_bot=False, first_name="Test User", username="testuser")


@pytest.fixture
def mock_chat() -> Chat:
    """Создает мок чата Telegram"""
    return Chat(id=123456, type="private")


@pytest.fixture
def mock_message(mock_user: User, mock_chat: Chat) -> Message:
    """Создает мок сообщения Telegram"""
    message = MagicMock(spec=Message)
    message.from_user = mock_user
    message.chat = mock_chat
    message.text = "Hello, bot!"
    message.answer = AsyncMock()
    return message


@pytest.fixture
def mock_llm_client() -> AsyncMock:
    """Создает мок LLM клиента"""
    client = AsyncMock()
    client.send_message = AsyncMock(return_value="Hello! How can I help you?")
    return client


@pytest.fixture
def mock_role_manager() -> MagicMock:
    """Создает мок менеджера ролей"""
    role_manager = MagicMock()
    role_manager.get_system_prompt.return_value = "You are a helpful assistant"
    role_manager.get_role_description.return_value = (
        "Ты - профессиональный ИИ-Нутрициолог с глубокими знаниями "
        "в области правильного питания, диетологии и здорового образа жизни."
    )
    return role_manager


@pytest.fixture
def mock_config() -> Config:
    """Создает мок конфигурации"""
    config = MagicMock(spec=Config)
    config.welcome_message = "Welcome to AI Assistant!"
    config.default_system_prompt = "You are a helpful assistant"
    config.max_context_messages = 10
    config.max_storage_size = 1000
    config.storage_ttl_hours = 24
    return config


@pytest.fixture
def dependencies(
    mock_llm_client: AsyncMock, mock_role_manager: MagicMock, mock_config: Config
) -> BotDependencies:
    """Создает контейнер зависимостей для тестов"""
    return BotDependencies(
        user_storage=UserStorage(),
        conversation_storage=ConversationStorage(),
        llm_client=mock_llm_client,
        role_manager=mock_role_manager,
        config=mock_config,
    )


@pytest.mark.asyncio
async def test_cmd_start_creates_user_and_conversation(
    mock_message: Message, dependencies: BotDependencies
) -> None:
    """Тест команды /start - создание пользователя и диалога"""
    # Выполняем команду
    await cmd_start(mock_message, dependencies)

    # Проверяем что пользователь создан
    user = dependencies.user_storage.get(123456)
    assert user is not None
    assert user.chat_id == 123456
    assert user.username == "testuser"
    assert user.first_name == "Test User"

    # Проверяем что диалог создан
    conversation = dependencies.conversation_storage.get(123456)
    assert conversation is not None
    assert conversation.chat_id == 123456

    # Проверяем что отправлено приветственное сообщение
    mock_message.answer.assert_called_once()
    call_args = mock_message.answer.call_args[0][0]
    assert "Test User" in call_args
    assert "Welcome to AI Assistant!" in call_args


@pytest.mark.asyncio
async def test_cmd_clear_clears_conversation(
    mock_message: Message, dependencies: BotDependencies
) -> None:
    """Тест команды /clear - очистка истории диалога"""
    # Создаем диалог с сообщениями
    conversation = dependencies.conversation_storage.get_or_create(123456)
    conversation.add_message("user", "Message 1")
    conversation.add_message("assistant", "Response 1")
    conversation.add_message("user", "Message 2")
    assert len(conversation.messages) == 3

    # Выполняем команду clear
    await cmd_clear(mock_message, dependencies)

    # Проверяем что история очищена
    assert len(conversation.messages) == 0

    # Проверяем что отправлено сообщение об очистке
    mock_message.answer.assert_called_once()
    call_args = mock_message.answer.call_args[0][0]
    assert "очищена" in call_args.lower()


@pytest.mark.asyncio
async def test_message_handler_full_flow(
    mock_message: Message, dependencies: BotDependencies, mock_llm_client: AsyncMock
) -> None:
    """Тест полного flow обработки сообщения"""
    # Выполняем обработку сообщения
    await message_handler(mock_message, dependencies)

    # Проверяем что пользователь создан
    user = dependencies.user_storage.get(123456)
    assert user is not None

    # Проверяем что LLM клиент был вызван
    mock_llm_client.send_message.assert_called_once()

    # Проверяем что ответ был отправлен пользователю
    mock_message.answer.assert_called_once_with("Hello! How can I help you?")

    # Проверяем что оба сообщения (user + assistant) добавлены в диалог
    conversation = dependencies.conversation_storage.get(123456)
    assert conversation is not None
    assert len(conversation.messages) == 2
    assert conversation.messages[0]["role"] == "user"
    assert conversation.messages[0]["content"] == "Hello, bot!"
    assert conversation.messages[1]["role"] == "assistant"
    assert conversation.messages[1]["content"] == "Hello! How can I help you?"


@pytest.mark.asyncio
async def test_message_handler_with_context(
    mock_message: Message, dependencies: BotDependencies, mock_llm_client: AsyncMock
) -> None:
    """Тест обработки сообщения с учетом контекста"""
    # Создаем диалог с предыдущими сообщениями
    conversation = dependencies.conversation_storage.get_or_create(123456)
    conversation.add_message("user", "What is Python?")
    conversation.add_message("assistant", "Python is a programming language.")

    mock_message.text = "Tell me more"

    # Выполняем обработку
    await message_handler(mock_message, dependencies)

    # Проверяем что LLM получил контекст
    mock_llm_client.send_message.assert_called_once()
    context = mock_llm_client.send_message.call_args[0][0]

    # Контекст должен содержать system prompt + предыдущие сообщения + новое
    assert len(context) >= 3
    assert context[0]["role"] == "system"
    assert any(msg["content"] == "What is Python?" for msg in context)
    assert any(msg["content"] == "Tell me more" for msg in context)


@pytest.mark.asyncio
async def test_message_handler_llm_error(
    mock_message: Message, dependencies: BotDependencies, mock_llm_client: AsyncMock
) -> None:
    """Тест обработки ошибки LLM"""
    # Настраиваем LLM клиент на ошибку
    mock_llm_client.send_message = AsyncMock(side_effect=Exception("LLM API error"))

    # Выполняем обработку
    await message_handler(mock_message, dependencies)

    # Проверяем что пользователю отправлено сообщение об ошибке
    mock_message.answer.assert_called_once()
    error_message = mock_message.answer.call_args[0][0]
    assert "ошибка" in error_message.lower()

    # Проверяем что сообщение пользователя НЕ осталось в истории
    conversation = dependencies.conversation_storage.get(123456)
    assert len(conversation.messages) == 0


@pytest.mark.asyncio
async def test_message_handler_without_user(dependencies: BotDependencies) -> None:
    """Тест обработки сообщения без from_user"""
    message = MagicMock(spec=Message)
    message.from_user = None
    message.answer = AsyncMock()

    # Выполняем обработку
    await message_handler(message, dependencies)

    # Проверяем что ничего не произошло
    message.answer.assert_not_called()


@pytest.mark.asyncio
async def test_message_handler_validation_too_long(
    mock_message: Message, dependencies: BotDependencies
) -> None:
    """Тест валидации - слишком длинное сообщение"""
    # Создаем очень длинное сообщение (>4000 символов)
    mock_message.text = "a" * 5000

    # Выполняем обработку
    await message_handler(mock_message, dependencies)

    # Проверяем что отправлено сообщение об ошибке валидации
    mock_message.answer.assert_called_once()
    error_message = mock_message.answer.call_args[0][0]
    assert "длинное" in error_message.lower() or "4000" in error_message

    # Проверяем что сообщение НЕ добавлено в диалог
    conversation = dependencies.conversation_storage.get(123456)
    if conversation:
        assert len(conversation.messages) == 0


@pytest.mark.asyncio
async def test_message_handler_validation_empty(
    mock_message: Message, dependencies: BotDependencies
) -> None:
    """Тест валидации - пустое сообщение"""
    mock_message.text = ""

    # Выполняем обработку
    await message_handler(mock_message, dependencies)

    # Проверяем что отправлено сообщение об ошибке
    mock_message.answer.assert_called_once()
    error_message = mock_message.answer.call_args[0][0]
    assert "пуст" in error_message.lower()  # "пустым" или "пустое"


@pytest.mark.asyncio
async def test_cmd_role_shows_description(
    mock_message: Message, dependencies: BotDependencies
) -> None:
    """🔴 RED: Тест команды /role - показ описания роли"""
    # Импортируем cmd_role (который еще не существует)
    from src.handlers.handlers import cmd_role

    # Выполняем команду
    await cmd_role(mock_message, dependencies)

    # Проверяем что ответ содержит описание роли
    mock_message.answer.assert_called_once()
    response = mock_message.answer.call_args[0][0]
    assert "Нутрициолог" in response
    assert "питани" in response.lower()


@pytest.mark.asyncio
async def test_cmd_help_shows_commands(mock_message: Message) -> None:
    """🔴 RED: Тест команды /help - показ списка команд"""
    # Импортируем cmd_help (который еще не существует)
    from src.handlers.handlers import cmd_help

    # Выполняем команду
    await cmd_help(mock_message)

    # Проверяем что ответ содержит список команд
    mock_message.answer.assert_called_once()
    response = mock_message.answer.call_args[0][0]
    assert "/start" in response
    assert "/clear" in response
    assert "/role" in response
    assert "/help" in response
