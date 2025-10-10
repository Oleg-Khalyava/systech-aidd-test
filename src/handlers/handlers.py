"""Обработчики команд и сообщений Telegram бота"""

import logging
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from src.config import Config
from src.user import UserStorage
from src.conversation import ConversationStorage
from llm.client import LLMClient

router = Router()
logger = logging.getLogger("telegram_bot")

# Глобальные хранилища и клиент (будут инициализированы в main.py)
user_storage: UserStorage
conversation_storage: ConversationStorage
llm_client: LLMClient
config: Config


def init_handlers(
    us: UserStorage, cs: ConversationStorage, llm: LLMClient, cfg: Config
) -> None:
    """Инициализация глобальных объектов для handlers
    
    Args:
        us: Хранилище пользователей
        cs: Хранилище диалогов
        llm: LLM клиент
        cfg: Конфигурация
    """
    global user_storage, conversation_storage, llm_client, config
    user_storage = us
    conversation_storage = cs
    llm_client = llm
    config = cfg


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    """Обработчик команды /start - приветствие и инициализация пользователя
    
    Args:
        message: Сообщение от пользователя
    """
    if not message.from_user:
        return
    
    logger.info(
        f"Received /start command from user {message.from_user.id} "
        f"(@{message.from_user.username}, {message.from_user.first_name})"
    )
    
    # Создаем или получаем пользователя
    user = user_storage.get_or_create(
        chat_id=message.chat.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        default_role=config.default_system_prompt,
    )
    
    # Создаем или получаем диалог
    conversation_storage.get_or_create(message.chat.id)
    
    # Отправляем приветствие из конфига с именем пользователя
    await message.answer(f"Привет, {user.first_name}! {config.welcome_message}")


@router.message(Command("clear"))
async def cmd_clear(message: Message) -> None:
    """Обработчик команды /clear - очистка истории диалога
    
    Args:
        message: Сообщение от пользователя
    """
    logger.info(f"Received /clear command from user {message.from_user.id if message.from_user else 'unknown'}")
    
    conversation = conversation_storage.get(message.chat.id)
    
    if conversation:
        messages_count = len(conversation.messages)
        conversation.clear()
        logger.info(f"Cleared conversation history for chat {message.chat.id} ({messages_count} messages)")
        await message.answer("✅ История диалога очищена. Начнем сначала!")
    else:
        await message.answer("История диалога уже пуста.")


@router.message()
async def message_handler(message: Message) -> None:
    """Обработчик текстовых сообщений
    
    Args:
        message: Сообщение от пользователя
    """
    if not message.text or not message.from_user:
        return
    
    logger.info(
        f"Received message from user {message.from_user.id} "
        f"(@{message.from_user.username}): {message.text[:50]}{'...' if len(message.text) > 50 else ''}"
    )
    
    # Получаем пользователя и диалог
    user = user_storage.get_or_create(
        chat_id=message.chat.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        default_role=config.default_system_prompt,
    )
    conversation = conversation_storage.get_or_create(message.chat.id)
    
    # Добавляем сообщение пользователя в историю
    conversation.add_message("user", message.text)
    
    try:
        # Формируем контекст для LLM
        context = conversation.get_context(
            max_messages=config.max_context_messages,
            system_prompt=user.current_role,
        )
        
        # Отправляем запрос к LLM
        response = await llm_client.send_message(context)
        
        # Добавляем ответ в историю
        conversation.add_message("assistant", response)
        
        logger.info(
            f"Successfully processed message for user {message.from_user.id}, "
            f"response length: {len(response)} chars"
        )
        
        # Отправляем ответ пользователю
        await message.answer(response)
        
    except Exception as e:
        logger.error(
            f"Error processing message from user {message.from_user.id}: {e}",
            exc_info=True
        )
        await message.answer(f"Произошла ошибка при обработке запроса: {e}")
        # Удаляем последнее сообщение пользователя из истории при ошибке
        if conversation.messages and conversation.messages[-1]["role"] == "user":
            conversation.messages.pop()

