"""Класс для управления пользователями"""

from dataclasses import dataclass


@dataclass
class User:
    """Пользователь бота
    
    Attributes:
        chat_id: ID чата в Telegram
        username: Username пользователя
        first_name: Имя пользователя
        current_role: Текущий системный промпт
    """
    chat_id: int
    username: str | None
    first_name: str
    current_role: str


class UserStorage:
    """In-memory хранилище пользователей"""
    
    def __init__(self):
        """Инициализация хранилища"""
        self._users: dict[int, User] = {}
    
    def get_or_create(
        self, chat_id: int, username: str | None, first_name: str, default_role: str
    ) -> User:
        """Получить пользователя или создать нового
        
        Args:
            chat_id: ID чата
            username: Username
            first_name: Имя
            default_role: Роль по умолчанию
            
        Returns:
            User: Объект пользователя
        """
        if chat_id not in self._users:
            self._users[chat_id] = User(
                chat_id=chat_id,
                username=username,
                first_name=first_name,
                current_role=default_role,
            )
        return self._users[chat_id]
    
    def get(self, chat_id: int) -> User | None:
        """Получить пользователя по chat_id
        
        Args:
            chat_id: ID чата
            
        Returns:
            User | None: Объект пользователя или None
        """
        return self._users.get(chat_id)

