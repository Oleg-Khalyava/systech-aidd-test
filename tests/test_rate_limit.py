"""Тесты для RateLimitMiddleware"""

import time
from unittest.mock import AsyncMock, MagicMock

import pytest
from aiogram.types import Chat, Message, User

from src.middlewares.rate_limit import RateLimitMiddleware


@pytest.fixture
def mock_user() -> User:
    """Создает мок пользователя"""
    return User(id=12345, is_bot=False, first_name="Test", username="testuser")


@pytest.fixture
def mock_chat() -> Chat:
    """Создает мок чата"""
    return Chat(id=12345, type="private")


@pytest.fixture
def mock_message(mock_user: User, mock_chat: Chat) -> Message:
    """Создает мок сообщения"""
    message = MagicMock(spec=Message)
    message.from_user = mock_user
    message.chat = mock_chat
    message.text = "Test message"
    message.answer = AsyncMock()
    return message


@pytest.fixture
def mock_handler() -> AsyncMock:
    """Создает мок handler'а"""
    return AsyncMock(return_value=None)


@pytest.fixture
def middleware() -> RateLimitMiddleware:
    """Создает middleware с лимитом 1 секунда"""
    return RateLimitMiddleware(rate_limit=1.0)


@pytest.mark.asyncio
async def test_rate_limit_first_message_passes(
    middleware: RateLimitMiddleware, mock_handler: AsyncMock, mock_message: Message
) -> None:
    """Тест что первое сообщение пропускается"""
    # Первое сообщение должно пройти
    await middleware(mock_handler, mock_message, {})

    # Handler должен быть вызван
    mock_handler.assert_called_once_with(mock_message, {})
    # Не должно быть ответа об ограничении
    mock_message.answer.assert_not_called()


@pytest.mark.asyncio
async def test_rate_limit_blocks_rapid_messages(
    middleware: RateLimitMiddleware, mock_handler: AsyncMock, mock_message: Message
) -> None:
    """Тест что быстрые сообщения блокируются"""
    # Первое сообщение
    await middleware(mock_handler, mock_message, {})
    assert mock_handler.call_count == 1

    # Второе сообщение сразу же (должно быть заблокировано)
    await middleware(mock_handler, mock_message, {})

    # Handler не должен быть вызван второй раз
    assert mock_handler.call_count == 1

    # Пользователь должен получить сообщение о лимите
    mock_message.answer.assert_called_once()
    warning_message = mock_message.answer.call_args[0][0]
    assert "подожд" in warning_message.lower() or "сек" in warning_message.lower()


@pytest.mark.asyncio
async def test_rate_limit_allows_after_timeout(
    mock_handler: AsyncMock, mock_message: Message
) -> None:
    """Тест что сообщение пропускается после истечения лимита"""
    # Создаем middleware с очень коротким лимитом
    middleware = RateLimitMiddleware(rate_limit=0.1)  # 100ms

    # Первое сообщение
    await middleware(mock_handler, mock_message, {})
    assert mock_handler.call_count == 1

    # Ждем больше лимита
    time.sleep(0.15)

    # Второе сообщение должно пройти
    await middleware(mock_handler, mock_message, {})
    assert mock_handler.call_count == 2

    # Не должно быть предупреждения
    mock_message.answer.assert_not_called()


@pytest.mark.asyncio
async def test_rate_limit_different_users(
    middleware: RateLimitMiddleware, mock_handler: AsyncMock, mock_chat: Chat
) -> None:
    """Тест что разные пользователи не влияют друг на друга"""
    # Создаем сообщения от разных пользователей
    user1 = User(id=1, is_bot=False, first_name="User1")
    user2 = User(id=2, is_bot=False, first_name="User2")

    message1 = MagicMock(spec=Message)
    message1.from_user = user1
    message1.chat = mock_chat
    message1.answer = AsyncMock()

    message2 = MagicMock(spec=Message)
    message2.from_user = user2
    message2.chat = mock_chat
    message2.answer = AsyncMock()

    # Оба сообщения должны пройти, так как от разных пользователей
    await middleware(mock_handler, message1, {})
    await middleware(mock_handler, message2, {})

    # Handler должен быть вызван для обоих
    assert mock_handler.call_count == 2
    message1.answer.assert_not_called()
    message2.answer.assert_not_called()


@pytest.mark.asyncio
async def test_rate_limit_without_user(
    middleware: RateLimitMiddleware, mock_handler: AsyncMock
) -> None:
    """Тест обработки сообщения без from_user"""
    message = MagicMock(spec=Message)
    message.from_user = None

    # Сообщение без пользователя должно пройти
    await middleware(mock_handler, message, {})

    # Handler должен быть вызван
    mock_handler.assert_called_once_with(message, {})


@pytest.mark.asyncio
async def test_rate_limit_custom_limit() -> None:
    """Тест кастомного лимита"""
    middleware = RateLimitMiddleware(rate_limit=2.0)  # 2 секунды

    user = User(id=999, is_bot=False, first_name="Test")
    chat = Chat(id=999, type="private")
    message = MagicMock(spec=Message)
    message.from_user = user
    message.chat = chat
    message.answer = AsyncMock()

    handler = AsyncMock()

    # Первое сообщение
    await middleware(handler, message, {})
    assert handler.call_count == 1

    # Второе сообщение сразу (должно быть заблокировано из-за 2-секундного лимита)
    await middleware(handler, message, {})
    assert handler.call_count == 1
    message.answer.assert_called_once()


@pytest.mark.asyncio
async def test_rate_limit_message_content_in_warning(
    middleware: RateLimitMiddleware, mock_handler: AsyncMock, mock_message: Message
) -> None:
    """Тест что предупреждение содержит информацию о времени ожидания"""
    # Первое сообщение
    await middleware(mock_handler, mock_message, {})

    # Второе сообщение сразу
    await middleware(mock_handler, mock_message, {})

    # Проверяем содержание предупреждения
    mock_message.answer.assert_called_once()
    warning = mock_message.answer.call_args[0][0]
    assert "секунд" in warning.lower() or "подожд" in warning.lower()
