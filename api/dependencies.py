"""Dependency injection for FastAPI"""

from api.chat_manager import ChatManager
from api.collectors.real_collector import RealStatCollector
from api.protocols import StatCollectorProtocol
from llm.client import LLMClient
from src.config import Config
from src.database.repository import DatabaseManager


async def get_stat_collector() -> StatCollectorProtocol:
    """Get statistics collector instance

    Now returns RealStatCollector that fetches data from actual database.

    Returns:
        StatCollectorProtocol implementation
    """
    # Load config to get database path
    config = Config.load()

    # Create database manager
    db_manager = DatabaseManager(config.database_path)
    await db_manager.init()

    # Return real collector
    return RealStatCollector(db_manager)


async def get_chat_manager() -> ChatManager:
    """Get chat manager instance

    Creates LLMClient and DatabaseManager for ChatManager.

    Returns:
        ChatManager instance
    """
    # Load config
    config = Config.load()

    # Create LLM client
    llm_client = LLMClient(
        api_key=config.openrouter_api_key,
        base_url=config.openrouter_base_url,
        model=config.openrouter_model,
    )

    # Create database manager
    db_manager = DatabaseManager(config.database_path)
    await db_manager.init()

    # Create and return chat manager
    return ChatManager(llm_client, db_manager)
