"""Класс Telegram бота на основе aiogram"""

from aiogram import Bot, Dispatcher


class TelegramBot:
    """Telegram бот
    
    Attributes:
        bot: Экземпляр aiogram Bot
        dp: Диспетчер для обработки сообщений
    """
    
    def __init__(self, token: str):
        """Инициализация бота
        
        Args:
            token: Токен Telegram бота
        """
        self.bot = Bot(token=token)
        self.dp = Dispatcher()
    
    async def start(self) -> None:
        """Запуск бота (polling)"""
        await self.dp.start_polling(self.bot)
    
    async def stop(self) -> None:
        """Остановка бота"""
        await self.bot.session.close()

