"""Класс для управления диалогами"""

from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime, timedelta


@dataclass
class Conversation:
    """Диалог с пользователем

    Attributes:
        chat_id: ID чата
        messages: История сообщений
        created_at: Время создания диалога
        last_accessed: Время последнего доступа
    """

    chat_id: int
    messages: list[dict[str, str]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)

    def add_message(self, role: str, content: str) -> None:
        """Добавить сообщение в историю

        Args:
            role: Роль (user/assistant/system)
            content: Текст сообщения
        """
        self.messages.append({"role": role, "content": content})
        self.last_accessed = datetime.now()

    def get_context(self, max_messages: int, system_prompt: str) -> list[dict[str, str]]:
        """Получить контекст для LLM

        Args:
            max_messages: Максимальное количество сообщений в контексте
            system_prompt: Системный промпт

        Returns:
            list[dict]: Список сообщений для LLM
        """
        self.last_accessed = datetime.now()
        # Системный промпт
        context = [{"role": "system", "content": system_prompt}]
        # Последние max_messages сообщений
        context.extend(self.messages[-max_messages:])
        return context

    def clear(self) -> None:
        """Очистить историю диалога"""
        self.messages.clear()


class ConversationStorage:
    """In-memory хранилище диалогов с LRU cache и TTL

    Attributes:
        max_size: Максимальное количество диалогов в хранилище
        ttl_hours: Время жизни диалога в часах
    """

    def __init__(self, max_size: int = 1000, ttl_hours: int = 24):
        """Инициализация хранилища

        Args:
            max_size: Максимальное количество диалогов (по умолчанию 1000)
            ttl_hours: Время жизни диалога в часах (по умолчанию 24)
        """
        self._conversations: OrderedDict[int, Conversation] = OrderedDict()
        self.max_size = max_size
        self.ttl_hours = ttl_hours

    def _cleanup_old(self) -> None:
        """Удаление устаревших диалогов (TTL)"""
        now = datetime.now()
        ttl_delta = timedelta(hours=self.ttl_hours)

        # Собираем ключи для удаления
        keys_to_delete = [
            chat_id
            for chat_id, conv in self._conversations.items()
            if now - conv.last_accessed > ttl_delta
        ]

        # Удаляем устаревшие диалоги
        for chat_id in keys_to_delete:
            del self._conversations[chat_id]

    def _enforce_size_limit(self) -> None:
        """Удаление старых диалогов при превышении лимита (LRU)"""
        while len(self._conversations) >= self.max_size:
            # Удаляем самый старый (первый) элемент из OrderedDict
            self._conversations.popitem(last=False)

    def get_or_create(self, chat_id: int) -> Conversation:
        """Получить диалог или создать новый

        Args:
            chat_id: ID чата

        Returns:
            Conversation: Объект диалога
        """
        # Очистка устаревших диалогов
        self._cleanup_old()

        if chat_id not in self._conversations:
            # Проверка лимита перед добавлением
            self._enforce_size_limit()
            self._conversations[chat_id] = Conversation(chat_id=chat_id)
        else:
            # Перемещаем в конец (обновляем LRU)
            self._conversations.move_to_end(chat_id)

        return self._conversations[chat_id]

    def get(self, chat_id: int) -> Conversation | None:
        """Получить диалог по chat_id

        Args:
            chat_id: ID чата

        Returns:
            Conversation | None: Объект диалога или None
        """
        # Очистка устаревших диалогов
        self._cleanup_old()

        conversation = self._conversations.get(chat_id)
        if conversation:
            # Перемещаем в конец (обновляем LRU)
            self._conversations.move_to_end(chat_id)
        return conversation
