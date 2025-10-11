"""Точка входа приложения - запуск Telegram бота"""

import asyncio
import signal
import sys

from aiogram.exceptions import TelegramNetworkError

from llm.client import LLMClient
from src.bot import TelegramBot
from src.config import Config
from src.conversation import ConversationStorage
from src.dependencies import BotDependencies
from src.handlers.handlers import router
from src.logger import setup_logger
from src.middlewares import DependencyInjectionMiddleware, RateLimitMiddleware
from src.role_manager import RoleManager
from src.user import UserStorage

# Настройка логгера
logger = setup_logger()

# Константы для retry logic
MAX_RETRIES = 3
RETRY_DELAY = 5  # секунд


async def start_with_retry(bot: TelegramBot) -> None:
    """Запуск бота с автоматическим переподключением при сетевых сбоях

    Args:
        bot: Экземпляр TelegramBot

    Raises:
        Exception: Если не удалось подключиться после MAX_RETRIES попыток
    """
    retries = 0

    while retries < MAX_RETRIES:
        try:
            logger.info("Starting bot polling...")
            await bot.start()
            break  # Успешный запуск
        except TelegramNetworkError as e:
            retries += 1
            logger.warning(
                f"Telegram network error (attempt {retries}/{MAX_RETRIES}): {e}", exc_info=True
            )
            if retries < MAX_RETRIES:
                logger.info(f"Retrying in {RETRY_DELAY} seconds...")
                await asyncio.sleep(RETRY_DELAY)
            else:
                logger.error(f"Failed to connect after {MAX_RETRIES} attempts")
                raise


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

    # Инициализация хранилищ с LRU cache и TTL
    logger.info(
        f"Initializing storages (max_size={config.max_storage_size}, "
        f"ttl={config.storage_ttl_hours}h)..."
    )
    user_storage = UserStorage(max_size=config.max_storage_size, ttl_hours=config.storage_ttl_hours)
    conversation_storage = ConversationStorage(
        max_size=config.max_storage_size, ttl_hours=config.storage_ttl_hours
    )

    # Инициализация LLM клиента
    logger.info(f"Initializing LLM client with model: {config.openrouter_model}")
    llm_client = LLMClient(
        api_key=config.openrouter_api_key,
        base_url=config.openrouter_base_url,
        model=config.openrouter_model,
    )

    # Инициализация менеджера ролей
    logger.info(f"Initializing role manager from: {config.system_prompt_file}")
    try:
        role_manager = RoleManager(config.system_prompt_file)
        logger.info("Role manager initialized successfully")
    except (FileNotFoundError, ValueError) as e:
        logger.error(f"Failed to initialize role manager: {e}")
        print(f"Role manager initialization error: {e}")
        sys.exit(1)

    # Создание контейнера зависимостей
    logger.info("Setting up dependency injection...")
    dependencies = BotDependencies(
        user_storage=user_storage,
        conversation_storage=conversation_storage,
        llm_client=llm_client,
        role_manager=role_manager,
        config=config,
    )

    # Инициализация бота
    logger.info("Initializing Telegram bot...")
    bot = TelegramBot(config.telegram_bot_token)

    # Подключение middlewares
    logger.info("Setting up middlewares...")

    # 1. Dependency Injection - должен быть первым, чтобы добавить deps в data
    di_middleware = DependencyInjectionMiddleware(dependencies)
    bot.dp.message.middleware(di_middleware)
    logger.info("Dependency injection middleware enabled")

    # 2. Rate Limiting
    rate_limit_middleware = RateLimitMiddleware(rate_limit=2.0)
    bot.dp.message.middleware(rate_limit_middleware)
    logger.info("Rate limiting middleware enabled (2 seconds per message)")

    # Подключение роутера
    bot.dp.include_router(router)

    # Настройка graceful shutdown
    loop = asyncio.get_event_loop()

    def signal_handler() -> None:
        """Обработчик сигналов для graceful shutdown"""
        logger.info("Received shutdown signal, stopping bot...")
        print("\nShutting down bot...")
        asyncio.create_task(bot.stop())
        loop.stop()

    # Регистрация обработчиков сигналов (только для Unix-подобных систем)
    if sys.platform != "win32":
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, signal_handler)

    # Запуск бота с retry logic
    print("Bot started. Press Ctrl+C to stop.")
    try:
        await start_with_retry(bot)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user (KeyboardInterrupt)")
        print("\nBot stopped by user")
    except TelegramNetworkError as e:
        logger.error(f"Failed to start bot due to network error: {e}", exc_info=True)
        print("\nFailed to connect to Telegram. Please check your internet connection.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error during bot operation: {e}", exc_info=True)
        raise
    finally:
        logger.info("Shutting down bot...")
        await bot.stop()
        logger.info("Bot stopped successfully")


if __name__ == "__main__":
    asyncio.run(main())
