"""Тесты для класса Config"""

from unittest.mock import patch

import pytest

from src.config import Config


@pytest.fixture(autouse=True)
def clear_env_vars(monkeypatch):
    """Очищает переменные окружения перед каждым тестом"""
    # Удаляем все переменные, которые могут повлиять на тесты
    env_vars = [
        "TELEGRAM_BOT_TOKEN",
        "OPENROUTER_API_KEY",
        "OPENROUTER_BASE_URL",
        "OPENROUTER_MODEL",
        "DEFAULT_SYSTEM_PROMPT",
        "MAX_CONTEXT_MESSAGES",
        "WELCOME_MESSAGE"
    ]
    for var in env_vars:
        monkeypatch.delenv(var, raising=False)

    # Мокаем load_dotenv чтобы она не загружала переменные из .env файла
    with patch('src.config.load_dotenv'):
        yield


def test_config_load_with_valid_env(monkeypatch):
    """Тест загрузки конфигурации с валидными переменными окружения"""
    # Устанавливаем тестовые переменные окружения
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11")
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-test-key-123456")
    monkeypatch.setenv("OPENROUTER_BASE_URL", "https://api.test.com")
    monkeypatch.setenv("OPENROUTER_MODEL", "test-model")
    monkeypatch.setenv("DEFAULT_SYSTEM_PROMPT", "Test prompt")
    monkeypatch.setenv("MAX_CONTEXT_MESSAGES", "20")
    monkeypatch.setenv("WELCOME_MESSAGE", "Test welcome")

    config = Config.load()

    assert config.telegram_bot_token == "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
    assert config.openrouter_api_key == "sk-test-key-123456"
    assert config.openrouter_base_url == "https://api.test.com"
    assert config.openrouter_model == "test-model"
    assert config.default_system_prompt == "Test prompt"
    assert config.max_context_messages == 20
    assert config.welcome_message == "Test welcome"


def test_config_load_with_default_values(monkeypatch):
    """Тест загрузки конфигурации со значениями по умолчанию"""
    # Устанавливаем только обязательные параметры
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")

    config = Config.load()

    assert config.telegram_bot_token == "test-token"
    assert config.openrouter_api_key == "test-key"
    assert config.openrouter_base_url == "https://openrouter.ai/api/v1"
    assert config.openrouter_model == "gpt-oss-20b"
    assert config.default_system_prompt == "Ты полезный AI-ассистент"
    assert config.max_context_messages == 10
    assert "AI-ассистент" in config.welcome_message


def test_config_missing_telegram_token(monkeypatch):
    """Тест ошибки при отсутствии токена Telegram"""
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)

    with pytest.raises(ValueError, match="TELEGRAM_BOT_TOKEN is required"):
        Config.load()


def test_config_missing_openrouter_key(monkeypatch):
    """Тест ошибки при отсутствии ключа OpenRouter"""
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

    with pytest.raises(ValueError, match="OPENROUTER_API_KEY is required"):
        Config.load()


def test_config_empty_telegram_token(monkeypatch):
    """Тест ошибки при пустом токене Telegram"""
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "   ")
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")

    with pytest.raises(ValueError, match="TELEGRAM_BOT_TOKEN cannot be empty"):
        Config.load()


def test_config_empty_openrouter_key(monkeypatch):
    """Тест ошибки при пустом ключе OpenRouter"""
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
    monkeypatch.setenv("OPENROUTER_API_KEY", "   ")

    with pytest.raises(ValueError, match="OPENROUTER_API_KEY cannot be empty"):
        Config.load()


def test_config_invalid_max_context_messages(monkeypatch):
    """Тест ошибки при неверном формате MAX_CONTEXT_MESSAGES"""
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.setenv("MAX_CONTEXT_MESSAGES", "not-a-number")

    with pytest.raises(ValueError, match="must be a valid integer"):
        Config.load()


def test_config_negative_max_context_messages(monkeypatch):
    """Тест ошибки при отрицательном значении MAX_CONTEXT_MESSAGES"""
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.setenv("MAX_CONTEXT_MESSAGES", "-5")

    with pytest.raises(ValueError, match="must be greater than 0"):
        Config.load()


def test_config_zero_max_context_messages(monkeypatch):
    """Тест ошибки при нулевом значении MAX_CONTEXT_MESSAGES"""
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.setenv("MAX_CONTEXT_MESSAGES", "0")

    with pytest.raises(ValueError, match="must be greater than 0"):
        Config.load()


def test_config_strips_whitespace(monkeypatch):
    """Тест удаления пробелов из токенов"""
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "  test-token  ")
    monkeypatch.setenv("OPENROUTER_API_KEY", "  test-key  ")

    config = Config.load()

    assert config.telegram_bot_token == "test-token"
    assert config.openrouter_api_key == "test-key"


def test_config_storage_parameters_defaults(monkeypatch):
    """Тест значений по умолчанию для параметров storage"""
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")

    config = Config.load()

    # Проверяем значения по умолчанию
    assert config.max_storage_size == 1000
    assert config.storage_ttl_hours == 24


def test_config_storage_parameters_custom(monkeypatch):
    """Тест кастомных значений для параметров storage"""
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.setenv("MAX_STORAGE_SIZE", "500")
    monkeypatch.setenv("STORAGE_TTL_HOURS", "12")

    config = Config.load()

    assert config.max_storage_size == 500
    assert config.storage_ttl_hours == 12


def test_config_invalid_max_storage_size(monkeypatch):
    """Тест ошибки при некорректном MAX_STORAGE_SIZE"""
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.setenv("MAX_STORAGE_SIZE", "invalid")

    with pytest.raises(ValueError, match="must be a valid integer"):
        Config.load()


def test_config_negative_max_storage_size(monkeypatch):
    """Тест ошибки при отрицательном MAX_STORAGE_SIZE"""
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.setenv("MAX_STORAGE_SIZE", "-100")

    with pytest.raises(ValueError, match="must be greater than 0"):
        Config.load()


def test_config_zero_max_storage_size(monkeypatch):
    """Тест ошибки при нулевом MAX_STORAGE_SIZE"""
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.setenv("MAX_STORAGE_SIZE", "0")

    with pytest.raises(ValueError, match="must be greater than 0"):
        Config.load()


def test_config_invalid_storage_ttl(monkeypatch):
    """Тест ошибки при некорректном STORAGE_TTL_HOURS"""
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.setenv("STORAGE_TTL_HOURS", "invalid")

    with pytest.raises(ValueError, match="must be a valid integer"):
        Config.load()


def test_config_negative_storage_ttl(monkeypatch):
    """Тест ошибки при отрицательном STORAGE_TTL_HOURS"""
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.setenv("STORAGE_TTL_HOURS", "-10")

    with pytest.raises(ValueError, match="must be greater than 0"):
        Config.load()


def test_config_zero_storage_ttl(monkeypatch):
    """Тест ошибки при нулевом STORAGE_TTL_HOURS"""
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.setenv("STORAGE_TTL_HOURS", "0")

    with pytest.raises(ValueError, match="must be greater than 0"):
        Config.load()
