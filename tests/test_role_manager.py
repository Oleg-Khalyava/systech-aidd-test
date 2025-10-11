"""TDD тесты для RoleManager"""

import pytest

from src.role_manager import RoleManager


class TestRoleManager:
    """TDD тесты для менеджера ролей"""

    def test_load_prompt_from_file(self, tmp_path):
        """🔴 RED: Загрузка промпта из файла"""
        # Arrange
        prompt_file = tmp_path / "test_prompt.txt"
        prompt_file.write_text("Test system prompt", encoding="utf-8")

        # Act
        manager = RoleManager(prompt_file)

        # Assert
        assert manager.get_system_prompt() == "Test system prompt"

    def test_load_prompt_file_not_found(self):
        """🔴 RED: Ошибка при отсутствии файла"""
        # Act & Assert
        with pytest.raises(FileNotFoundError):
            RoleManager("nonexistent_file.txt")

    def test_load_prompt_empty_file(self, tmp_path):
        """🔴 RED: Ошибка при пустом файле"""
        # Arrange
        prompt_file = tmp_path / "empty.txt"
        prompt_file.write_text("   \n  \n", encoding="utf-8")

        # Act & Assert
        with pytest.raises(ValueError, match="empty"):
            RoleManager(prompt_file)

    def test_get_role_description(self, tmp_path):
        """🔴 RED: Получение описания роли"""
        # Arrange
        prompt_text = """Ты - профессиональный Нутрициолог.

Твоя специализация:
- Здоровое питание
- Диеты

Твой стиль: дружелюбный
"""
        prompt_file = tmp_path / "nutritionist.txt"
        prompt_file.write_text(prompt_text, encoding="utf-8")
        manager = RoleManager(prompt_file)

        # Act
        description = manager.get_role_description()

        # Assert
        assert "профессиональный Нутрициолог" in description
        assert len(description) > 0

    def test_reload_prompt(self, tmp_path):
        """🔴 RED: Перезагрузка промпта"""
        # Arrange
        prompt_file = tmp_path / "reload_test.txt"
        prompt_file.write_text("Original prompt", encoding="utf-8")
        manager = RoleManager(prompt_file)

        assert manager.get_system_prompt() == "Original prompt"

        # Act - изменяем файл
        prompt_file.write_text("Updated prompt", encoding="utf-8")
        manager.reload_prompt()

        # Assert
        assert manager.get_system_prompt() == "Updated prompt"

    def test_load_prompt_with_path_object(self, tmp_path):
        """🔴 RED: Поддержка Path объектов"""
        # Arrange
        prompt_file = tmp_path / "path_test.txt"
        prompt_file.write_text("Path object prompt", encoding="utf-8")

        # Act
        manager = RoleManager(prompt_file)

        # Assert
        assert manager.get_system_prompt() == "Path object prompt"

    def test_role_description_multiple_lines(self, tmp_path):
        """🔴 RED: Описание роли из многострочного промпта"""
        # Arrange
        prompt_text = """Line 1: Important info

Line 2: More info

Line 3: Additional

Line 4: Extra

Line 5: Even more

Line 6: Should not be included
"""
        prompt_file = tmp_path / "multiline.txt"
        prompt_file.write_text(prompt_text, encoding="utf-8")
        manager = RoleManager(prompt_file)

        # Act
        description = manager.get_role_description()

        # Assert
        assert "Line 1" in description
        assert "Line 5" in description
        # Должно быть не более 5 строк
        assert description.count("\n") <= 4
