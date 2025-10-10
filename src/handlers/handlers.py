"""Обработчики команд и сообщений Telegram бота"""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from src.config import Config
from src.user import UserStorage
from src.conversation import ConversationStorage
from llm.client import LLMClient

router = Router()

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
    """Обработчик команды /start
    
    Args:
        message: Сообщение от пользователя
    """
    if not message.from_user:
        return
    
    # Создаем или получаем пользователя
    user = user_storage.get_or_create(
        chat_id=message.chat.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        default_role=config.default_system_prompt,
    )
    
    # Создаем или получаем диалог
    conversation_storage.get_or_create(message.chat.id)
    
    await message.answer(
        f"Привет, {user.first_name}! Я AI-ассистент на базе LLM. "
        "Задавай любые вопросы, и я постараюсь помочь!"
    )


@router.message()
async def message_handler(message: Message) -> None:
    """Обработчик текстовых сообщений
    
    Args:
        message: Сообщение от пользователя
    """
    if not message.text or not message.from_user:
        return
    
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
        
        # Отправляем ответ пользователю
        await message.answer(response)
        
    except Exception as e:
        await message.answer(f"Произошла ошибка при обработке запроса: {e}")
        # Удаляем последнее сообщение пользователя из истории при ошибке
        if conversation.messages and conversation.messages[-1]["role"] == "user":
            conversation.messages.pop()

