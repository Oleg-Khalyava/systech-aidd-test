"""Repository layer for database access using direct SQL with aiosqlite"""

import logging
from pathlib import Path
from typing import Any

import aiosqlite

logger = logging.getLogger("telegram_bot")


class DatabaseManager:
    """Singleton database manager for SQLite connections

    Manages a single connection to the SQLite database with proper async support.
    All queries are executed using direct SQL without ORM.
    """

    _instance: "DatabaseManager | None" = None
    _connection: aiosqlite.Connection | None = None

    def __new__(cls, db_path: str = "data/bot.db") -> "DatabaseManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.db_path = db_path
        return cls._instance

    async def init(self) -> None:
        """Initialize database connection and configure SQLite

        Sets up:
        - Foreign key constraints (enabled)
        - WAL mode for better concurrency
        - Row factory for dict-like access
        """
        # Create data directory if not exists
        db_path = Path(self.db_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)

        # Open connection
        self._connection = await aiosqlite.connect(self.db_path)

        # Enable foreign keys
        await self._connection.execute("PRAGMA foreign_keys = ON")

        # Set WAL mode for better concurrency
        await self._connection.execute("PRAGMA journal_mode = WAL")

        # Set row factory to return dicts
        self._connection.row_factory = aiosqlite.Row

        logger.info(f"Database initialized: {self.db_path}")

    async def close(self) -> None:
        """Close database connection"""
        if self._connection:
            await self._connection.close()
            self._connection = None
            logger.info("Database connection closed")

    async def execute(self, query: str, params: tuple[Any, ...] = ()) -> aiosqlite.Cursor:
        """Execute SQL query

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            Cursor object

        Raises:
            RuntimeError: If connection not initialized
        """
        if not self._connection:
            raise RuntimeError("Database connection not initialized. Call init() first.")

        cursor = await self._connection.execute(query, params)
        await self._connection.commit()
        return cursor

    async def fetchone(self, query: str, params: tuple[Any, ...] = ()) -> dict[str, Any] | None:
        """Execute query and fetch one row as dict

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            Dict with row data or None if no results
        """
        if not self._connection:
            raise RuntimeError("Database connection not initialized. Call init() first.")

        cursor = await self._connection.execute(query, params)
        row = await cursor.fetchone()
        if row:
            return dict(row)
        return None

    async def fetchall(self, query: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        """Execute query and fetch all rows as list of dicts

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            List of dicts with row data
        """
        if not self._connection:
            raise RuntimeError("Database connection not initialized. Call init() first.")

        cursor = await self._connection.execute(query, params)
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


class UserRepository:
    """Repository for user data access using direct SQL"""

    def __init__(self, db_manager: DatabaseManager):
        """Initialize repository

        Args:
            db_manager: Database manager instance
        """
        self.db = db_manager

    async def get_or_create(
        self, chat_id: int, username: str | None, first_name: str
    ) -> dict[str, Any]:
        """Get existing user or create new one

        Uses INSERT OR IGNORE to avoid conflicts, then fetches the user.
        Updates last_accessed timestamp for existing users.

        Args:
            chat_id: Telegram chat ID
            username: Telegram username (can be None)
            first_name: User's first name

        Returns:
            Dict with user data
        """
        # Try to insert (will be ignored if exists)
        await self.db.execute(
            """
            INSERT OR IGNORE INTO users (id, username, first_name, created_at, last_accessed)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """,
            (chat_id, username, first_name),
        )

        # Update last_accessed for existing user
        await self.db.execute(
            """
            UPDATE users
            SET last_accessed = CURRENT_TIMESTAMP
            WHERE id = ? AND deleted_at IS NULL
            """,
            (chat_id,),
        )

        # Fetch and return user
        user = await self.db.fetchone(
            "SELECT * FROM users WHERE id = ? AND deleted_at IS NULL", (chat_id,)
        )

        if not user:
            raise RuntimeError(f"Failed to get or create user with chat_id={chat_id}")

        return user

    async def get_by_id(self, chat_id: int) -> dict[str, Any] | None:
        """Get user by chat_id

        Args:
            chat_id: Telegram chat ID

        Returns:
            Dict with user data or None if not found
        """
        return await self.db.fetchone(
            "SELECT * FROM users WHERE id = ? AND deleted_at IS NULL", (chat_id,)
        )

    async def update_last_accessed(self, chat_id: int) -> None:
        """Update last_accessed timestamp

        Args:
            chat_id: Telegram chat ID
        """
        await self.db.execute(
            """
            UPDATE users
            SET last_accessed = CURRENT_TIMESTAMP
            WHERE id = ? AND deleted_at IS NULL
            """,
            (chat_id,),
        )

    async def soft_delete(self, chat_id: int) -> None:
        """Soft delete user by setting deleted_at timestamp

        Args:
            chat_id: Telegram chat ID
        """
        await self.db.execute(
            """
            UPDATE users
            SET deleted_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (chat_id,),
        )


class MessageRepository:
    """Repository for message data access using direct SQL"""

    def __init__(self, db_manager: DatabaseManager):
        """Initialize repository

        Args:
            db_manager: Database manager instance
        """
        self.db = db_manager

    async def create(self, user_id: int, role: str, content: str) -> int:
        """Create new message

        Automatically calculates length field from content.

        Args:
            user_id: User's chat ID
            role: Message role ('user', 'assistant', 'system')
            content: Message content

        Returns:
            ID of created message
        """
        length = len(content)
        cursor = await self.db.execute(
            """
            INSERT INTO messages (user_id, role, content, length, created_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """,
            (user_id, role, content, length),
        )
        if cursor.lastrowid is None:
            raise RuntimeError("Failed to create message: no lastrowid returned")
        return cursor.lastrowid

    async def get_recent(self, user_id: int, limit: int) -> list[dict[str, Any]]:
        """Get recent messages for user

        Returns messages ordered by created_at DESC (most recent first).

        Args:
            user_id: User's chat ID
            limit: Maximum number of messages to return

        Returns:
            List of message dicts (most recent first)
        """
        return await self.db.fetchall(
            """
            SELECT * FROM messages
            WHERE user_id = ? AND deleted_at IS NULL
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (user_id, limit),
        )

    async def soft_delete(self, message_id: int) -> None:
        """Soft delete message by setting deleted_at timestamp

        Args:
            message_id: Message ID
        """
        await self.db.execute(
            """
            UPDATE messages
            SET deleted_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (message_id,),
        )

    async def soft_delete_all_for_user(self, user_id: int) -> None:
        """Soft delete all messages for user

        Used for /clear command.

        Args:
            user_id: User's chat ID
        """
        await self.db.execute(
            """
            UPDATE messages
            SET deleted_at = CURRENT_TIMESTAMP
            WHERE user_id = ? AND deleted_at IS NULL
            """,
            (user_id,),
        )

    async def search_fts(self, query: str) -> list[dict[str, Any]]:
        """Full-text search in messages using FTS5

        Args:
            query: Search query

        Returns:
            List of matching message dicts
        """
        return await self.db.fetchall(
            """
            SELECT m.* FROM messages m
            JOIN messages_fts fts ON m.id = fts.rowid
            WHERE messages_fts MATCH ? AND m.deleted_at IS NULL
            ORDER BY m.created_at DESC
            """,
            (query,),
        )
