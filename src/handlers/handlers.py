"""Обработчики команд и сообщений Telegram бота"""

import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.dependencies import BotDependencies
from src.validators import MessageValidator

router = Router()
logger = logging.getLogger("telegram_bot")

# Инициализируем валидатор сообщений (не зависит от конфигурации)
message_validator = MessageValidator()


@router.message(Command("start"))
async def cmd_start(message: Message, deps: BotDependencies) -> None:
    """Обработчик команды /start - приветствие и инициализация пользователя

    Args:
        message: Сообщение от пользователя
        deps: Контейнер с зависимостями бота
    """
    if not message.from_user:
        return

    logger.info(
        f"Received /start command from user {message.from_user.id} "
        f"(@{message.from_user.username}, {message.from_user.first_name})"
    )

    # Создаем или получаем пользователя
    user = await deps.user_repo.get_or_create(
        chat_id=message.chat.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        current_role=deps.config.default_system_prompt,
    )

    # Отправляем приветствие из конфига с именем пользователя
    await message.answer(f"Привет, {user['first_name']}! {deps.config.welcome_message}")


@router.message(Command("clear"))
async def cmd_clear(message: Message, deps: BotDependencies) -> None:
    """Обработчик команды /clear - очистка истории диалога

    Args:
        message: Сообщение от пользователя
        deps: Контейнер с зависимостями бота
    """
    logger.info(
        f"Received /clear command from user {message.from_user.id if message.from_user else 'unknown'}"
    )

    # Получаем текущие сообщения для подсчета
    messages = await deps.message_repo.get_recent(message.chat.id, limit=10000)
    messages_count = len(messages)

    if messages_count > 0:
        # Soft delete всех сообщений пользователя
        await deps.message_repo.soft_delete_all_for_user(message.chat.id)
        logger.info(
            f"Cleared conversation history for chat {message.chat.id} ({messages_count} messages)"
        )
        await message.answer("✅ История диалога очищена. Начнем сначала!")
    else:
        await message.answer("История диалога уже пуста.")


@router.message(Command("role"))
async def cmd_role(message: Message, deps: BotDependencies) -> None:
    """Обработчик команды /role - показать роль бота

    Args:
        message: Сообщение от пользователя
        deps: Контейнер с зависимостями бота
    """
    logger.info(
        f"Received /role command from user {message.from_user.id if message.from_user else 'unknown'}"
    )

    # Получаем описание роли из role_manager
    description = deps.role_manager.get_role_description()

    # Отправляем описание пользователю
    await message.answer(f"🤖 **Моя роль:**\n\n{description}")


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    """Обработчик команды /help - список команд

    Args:
        message: Сообщение от пользователя
    """
    logger.info(
        f"Received /help command from user {message.from_user.id if message.from_user else 'unknown'}"
    )

    help_text = """📋 **Доступные команды:**

/start - Начать диалог с ботом
/clear - Очистить историю диалога
/role - Узнать роль и специализацию бота
/help - Показать это сообщение

💬 Просто напиши мне сообщение, и я помогу тебе!"""

    await message.answer(help_text)


@router.message()
async def message_handler(message: Message, deps: BotDependencies) -> None:
    """Обработчик текстовых сообщений

    Args:
        message: Сообщение от пользователя
        deps: Контейнер с зависимостями бота
    """
    if not message.from_user:
        return

    # Валидация сообщения
    is_valid, error_message = message_validator.validate(message.text)
    if not is_valid:
        if error_message:
            await message.answer(error_message)
        return

    # После валидации message.text гарантированно str
    text = message.text
    if text is None:  # type guard
        return

    logger.info(
        f"Received message from user {message.from_user.id} "
        f"(@{message.from_user.username}): {text[:50]}{'...' if len(text) > 50 else ''}"
    )

    # Получаем или создаем пользователя (для трекинга)
    await deps.user_repo.get_or_create(
        chat_id=message.chat.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        current_role=deps.config.default_system_prompt,
    )

    # Сохраняем сообщение пользователя в БД
    user_message_id = await deps.message_repo.create(
        user_id=message.chat.id, role="user", content=text
    )

    try:
        # Получаем последние сообщения из БД
        recent_messages = await deps.message_repo.get_recent(
            user_id=message.chat.id, limit=deps.config.max_context_messages
        )

        # Формируем контекст для LLM (сообщения в обратном порядке - от старых к новым)
        context = [{"role": "system", "content": deps.role_manager.get_system_prompt()}]
        context.extend(
            [{"role": msg["role"], "content": msg["content"]} for msg in reversed(recent_messages)]
        )

        # Отправляем запрос к LLM
        response = await deps.llm_client.send_message(context)

        # Сохраняем ответ ассистента в БД
        await deps.message_repo.create(user_id=message.chat.id, role="assistant", content=response)

        logger.info(
            f"Successfully processed message for user {message.from_user.id}, "
            f"response length: {len(response)} chars"
        )

        # Отправляем ответ пользователю
        await message.answer(response)

    except Exception as e:
        logger.error(
            f"Error processing message from user {message.from_user.id}: {e}", exc_info=True
        )
        # Не раскрываем детали внутренних ошибок пользователю
        await message.answer(
            "😔 Извините, произошла ошибка при обработке вашего запроса. Попробуйте еще раз."
        )
        # Удаляем сообщение пользователя из БД при ошибке (soft delete)
        await deps.message_repo.soft_delete(user_message_id)
