"""Настройка логирования для бота"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logger() -> logging.Logger:
    """Настройка логгера с ротацией файлов

    Returns:
        logging.Logger: Настроенный логгер
    """
    # Создаем директорию logs если её нет
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Создаем логгер
    logger = logging.getLogger("telegram_bot")
    logger.setLevel(logging.INFO)

    # Если уже есть handlers, не добавляем повторно
    if logger.handlers:
        return logger

    # Формат записи
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Файловый handler с ротацией (10MB, 5 файлов)
    file_handler = RotatingFileHandler(
        logs_dir / "bot.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # Консольный handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Добавляем handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

