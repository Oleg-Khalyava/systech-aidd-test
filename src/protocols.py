"""Protocol интерфейсы для Dependency Inversion"""

from typing import Protocol


class ILLMClient(Protocol):
    """Интерфейс для клиента LLM

    Определяет контракт для работы с LLM сервисом.
    """

    async def send_message(self, messages: list[dict[str, str]]) -> str:
        """Отправка сообщения в LLM

        Args:
            messages: История сообщений в формате OpenAI

        Returns:
            str: Ответ от LLM

        Raises:
            Exception: При ошибках API
        """
        ...


class IRoleManager(Protocol):
    """Интерфейс для менеджера ролей

    Определяет контракт для работы с системными промптами.
    """

    def get_system_prompt(self) -> str:
        """Получить системный промпт

        Returns:
            str: Системный промпт для LLM
        """
        ...

    def get_role_description(self) -> str:
        """Получить описание роли для пользователя

        Returns:
            str: Человекочитаемое описание роли
        """
        ...

    def reload_prompt(self) -> None:
        """Перезагрузить промпт из файла

        Raises:
            FileNotFoundError: Если файл не найден
            ValueError: Если файл пустой
        """
        ...
