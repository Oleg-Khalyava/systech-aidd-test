"""Точка входа приложения - запуск Telegram бота"""

import asyncio
import signal
import sys
from src.config import Config
from src.bot import TelegramBot
from src.user import UserStorage
from src.conversation import ConversationStorage
from src.handlers.handlers import router, init_handlers
from llm.client import LLMClient


async def main() -> None:
    """Главная функция запуска бота"""
    # Загрузка конфигурации
    try:
        config = Config.load()
    except ValueError as e:
        print(f"Configuration error: {e}")
        sys.exit(1)
    
    # Инициализация хранилищ
    user_storage = UserStorage()
    conversation_storage = ConversationStorage()
    
    # Инициализация LLM клиента
    llm_client = LLMClient(
        api_key=config.openrouter_api_key,
        base_url=config.openrouter_base_url,
        model=config.openrouter_model,
    )
    
    # Инициализация handlers с зависимостями
    init_handlers(user_storage, conversation_storage, llm_client, config)
    
    # Инициализация бота
    bot = TelegramBot(config.telegram_bot_token)
    bot.dp.include_router(router)
    
    # Настройка graceful shutdown
    loop = asyncio.get_event_loop()
    
    def signal_handler():
        """Обработчик сигналов для graceful shutdown"""
        print("\nShutting down bot...")
        asyncio.create_task(bot.stop())
        loop.stop()
    
    # Регистрация обработчиков сигналов (только для Unix-подобных систем)
    if sys.platform != "win32":
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, signal_handler)
    
    # Запуск бота
    print("Bot started. Press Ctrl+C to stop.")
    try:
        await bot.start()
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    finally:
        await bot.stop()


if __name__ == "__main__":
    asyncio.run(main())

