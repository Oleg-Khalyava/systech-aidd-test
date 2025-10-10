"""Класс для управления диалогами"""

from dataclasses import dataclass, field


@dataclass
class Conversation:
    """Диалог с пользователем
    
    Attributes:
        chat_id: ID чата
        messages: История сообщений
    """
    
    chat_id: int
    messages: list[dict] = field(default_factory=list)
    
    def add_message(self, role: str, content: str) -> None:
        """Добавить сообщение в историю
        
        Args:
            role: Роль (user/assistant/system)
            content: Текст сообщения
        """
        self.messages.append({"role": role, "content": content})
    
    def get_context(self, max_messages: int, system_prompt: str) -> list[dict]:
        """Получить контекст для LLM
        
        Args:
            max_messages: Максимальное количество сообщений в контексте
            system_prompt: Системный промпт
            
        Returns:
            list[dict]: Список сообщений для LLM
        """
        # Системный промпт
        context = [{"role": "system", "content": system_prompt}]
        # Последние max_messages сообщений
        context.extend(self.messages[-max_messages:])
        return context
    
    def clear(self) -> None:
        """Очистить историю диалога"""
        self.messages.clear()


class ConversationStorage:
    """In-memory хранилище диалогов"""
    
    def __init__(self):
        """Инициализация хранилища"""
        self._conversations: dict[int, Conversation] = {}
    
    def get_or_create(self, chat_id: int) -> Conversation:
        """Получить диалог или создать новый
        
        Args:
            chat_id: ID чата
            
        Returns:
            Conversation: Объект диалога
        """
        if chat_id not in self._conversations:
            self._conversations[chat_id] = Conversation(chat_id=chat_id)
        return self._conversations[chat_id]
    
    def get(self, chat_id: int) -> Conversation | None:
        """Получить диалог по chat_id
        
        Args:
            chat_id: ID чата
            
        Returns:
            Conversation | None: Объект диалога или None
        """
        return self._conversations.get(chat_id)

