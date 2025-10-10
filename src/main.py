"""Точка входа приложения - запуск Telegram бота"""

import asyncio
import signal
import sys
from src.config import Config
from src.bot import TelegramBot
from src.user import UserStorage
from src.conversation import ConversationStorage
from src.handlers.handlers import router, init_handlers
from src.logger import setup_logger
from llm.client import LLMClient

# Настройка логгера
logger = setup_logger()


async def main() -> None:
    """Главная функция запуска бота"""
    # Загрузка конфигурации
    try:
        logger.info("Loading configuration...")
        config = Config.load()
        logger.info("Configuration loaded successfully")
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        print(f"Configuration error: {e}")
        sys.exit(1)
    
    # Инициализация хранилищ
    logger.info("Initializing storages...")
    user_storage = UserStorage()
    conversation_storage = ConversationStorage()
    
    # Инициализация LLM клиента
    logger.info(f"Initializing LLM client with model: {config.openrouter_model}")
    llm_client = LLMClient(
        api_key=config.openrouter_api_key,
        base_url=config.openrouter_base_url,
        model=config.openrouter_model,
    )
    
    # Инициализация handlers с зависимостями
    init_handlers(user_storage, conversation_storage, llm_client, config)
    
    # Инициализация бота
    logger.info("Initializing Telegram bot...")
    bot = TelegramBot(config.telegram_bot_token)
    bot.dp.include_router(router)
    
    # Настройка graceful shutdown
    loop = asyncio.get_event_loop()
    
    def signal_handler():
        """Обработчик сигналов для graceful shutdown"""
        logger.info("Received shutdown signal, stopping bot...")
        print("\nShutting down bot...")
        asyncio.create_task(bot.stop())
        loop.stop()
    
    # Регистрация обработчиков сигналов (только для Unix-подобных систем)
    if sys.platform != "win32":
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, signal_handler)
    
    # Запуск бота
    logger.info("Starting bot polling...")
    print("Bot started. Press Ctrl+C to stop.")
    try:
        await bot.start()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user (KeyboardInterrupt)")
        print("\nBot stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error during bot operation: {e}", exc_info=True)
        raise
    finally:
        logger.info("Shutting down bot...")
        await bot.stop()
        logger.info("Bot stopped successfully")


if __name__ == "__main__":
    asyncio.run(main())

