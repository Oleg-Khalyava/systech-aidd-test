"""Менеджер для управления ролями и системными промптами бота"""

import logging
from pathlib import Path

logger = logging.getLogger("telegram_bot")


class RoleManager:
    """Менеджер ролей бота

    Управляет загрузкой и хранением системных промптов из файлов.
    Позволяет менять поведение бота без изменения кода.

    Attributes:
        _prompt_file: Путь к файлу с системным промптом
        _system_prompt: Текущий системный промпт
    """

    def __init__(self, prompt_file: str | Path):
        """Инициализация менеджера

        Args:
            prompt_file: Путь к файлу с системным промптом

        Raises:
            FileNotFoundError: Если файл не найден
            ValueError: Если файл пустой
        """
        self._prompt_file = Path(prompt_file)
        self._system_prompt = self._load_prompt()

    def _load_prompt(self) -> str:
        """Загружает промпт из файла

        Returns:
            str: Содержимое промпта

        Raises:
            FileNotFoundError: Если файл не найден
            ValueError: Если файл пустой
        """
        if not self._prompt_file.exists():
            raise FileNotFoundError(f"Prompt file not found: {self._prompt_file}")

        content = self._prompt_file.read_text(encoding="utf-8").strip()

        if not content:
            raise ValueError(f"Prompt file is empty: {self._prompt_file}")

        logger.info(f"Loaded system prompt from {self._prompt_file}")
        return content

    def get_system_prompt(self) -> str:
        """Получить текущий системный промпт

        Returns:
            str: Системный промпт
        """
        return self._system_prompt

    def get_role_description(self) -> str:
        """Получить краткое описание роли для отображения пользователю

        Returns:
            str: Описание роли в удобном формате
        """
        # Берем первые 5 непустых строк промпта как описание
        lines = [line.strip() for line in self._system_prompt.split("\n") if line.strip()]

        # Берем до 5 строк
        description_lines = lines[:5]

        return "\n".join(description_lines) if description_lines else "AI Assistant"

    def reload_prompt(self) -> None:
        """Перезагрузить промпт из файла

        Полезно для обновления поведения бота без перезапуска.

        Raises:
            FileNotFoundError: Если файл не найден
            ValueError: Если файл пустой
        """
        old_prompt = self._system_prompt
        self._system_prompt = self._load_prompt()

        if old_prompt != self._system_prompt:
            logger.info("System prompt reloaded successfully (changed)")
        else:
            logger.info("System prompt reloaded successfully (unchanged)")
