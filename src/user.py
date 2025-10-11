"""Класс для управления пользователями"""

from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime, timedelta


@dataclass
class User:
    """Пользователь бота

    Attributes:
        chat_id: ID чата в Telegram
        username: Username пользователя
        first_name: Имя пользователя
        current_role: Текущий системный промпт
        created_at: Время создания пользователя
        last_accessed: Время последнего доступа
    """

    chat_id: int
    username: str | None
    first_name: str
    current_role: str
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)


class UserStorage:
    """In-memory хранилище пользователей с LRU cache и TTL

    Attributes:
        max_size: Максимальное количество пользователей в хранилище
        ttl_hours: Время жизни пользователя в часах
    """

    def __init__(self, max_size: int = 1000, ttl_hours: int = 24):
        """Инициализация хранилища

        Args:
            max_size: Максимальное количество пользователей (по умолчанию 1000)
            ttl_hours: Время жизни пользователя в часах (по умолчанию 24)
        """
        self._users: OrderedDict[int, User] = OrderedDict()
        self.max_size = max_size
        self.ttl_hours = ttl_hours

    def _cleanup_old(self) -> None:
        """Удаление устаревших пользователей (TTL)"""
        now = datetime.now()
        ttl_delta = timedelta(hours=self.ttl_hours)

        # Собираем ключи для удаления
        keys_to_delete = [
            chat_id for chat_id, user in self._users.items() if now - user.last_accessed > ttl_delta
        ]

        # Удаляем устаревших пользователей
        for chat_id in keys_to_delete:
            del self._users[chat_id]

    def _enforce_size_limit(self) -> None:
        """Удаление старых пользователей при превышении лимита (LRU)"""
        while len(self._users) >= self.max_size:
            # Удаляем самого старого (первого) пользователя из OrderedDict
            self._users.popitem(last=False)

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
        # Очистка устаревших пользователей
        self._cleanup_old()

        if chat_id not in self._users:
            # Проверка лимита перед добавлением
            self._enforce_size_limit()
            self._users[chat_id] = User(
                chat_id=chat_id,
                username=username,
                first_name=first_name,
                current_role=default_role,
            )
        else:
            # Обновляем время последнего доступа
            self._users[chat_id].last_accessed = datetime.now()
            # Перемещаем в конец (обновляем LRU)
            self._users.move_to_end(chat_id)

        return self._users[chat_id]

    def get(self, chat_id: int) -> User | None:
        """Получить пользователя по chat_id

        Args:
            chat_id: ID чата

        Returns:
            User | None: Объект пользователя или None
        """
        # Очистка устаревших пользователей
        self._cleanup_old()

        user = self._users.get(chat_id)
        if user:
            # Обновляем время последнего доступа
            user.last_accessed = datetime.now()
            # Перемещаем в конец (обновляем LRU)
            self._users.move_to_end(chat_id)
        return user
