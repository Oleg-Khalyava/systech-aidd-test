"""Safe SQL executor for admin mode analytics"""

import logging
import re

from src.database.repository import DatabaseManager

logger = logging.getLogger("telegram_bot")


class SQLExecutor:
    """Execute SQL queries safely with validation

    Only allows SELECT queries with additional security checks.
    """

    # Dangerous SQL keywords that are not allowed
    DANGEROUS_KEYWORDS = [
        "INSERT",
        "UPDATE",
        "DELETE",
        "DROP",
        "CREATE",
        "ALTER",
        "TRUNCATE",
        "REPLACE",
        "EXEC",
        "EXECUTE",
        "PRAGMA",
    ]

    def __init__(self, db_manager: DatabaseManager):
        """Initialize SQL executor

        Args:
            db_manager: Database manager instance
        """
        self.db = db_manager

    def validate_sql(self, sql: str) -> tuple[bool, str]:
        """Validate SQL query for safety

        Args:
            sql: SQL query to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        sql_upper = sql.upper().strip()

        # Check if starts with SELECT
        if not sql_upper.startswith("SELECT"):
            return False, "Only SELECT queries are allowed"

        # Check for dangerous keywords
        for keyword in self.DANGEROUS_KEYWORDS:
            if re.search(rf"\b{keyword}\b", sql_upper):
                return False, f"Keyword '{keyword}' is not allowed"

        # Check for semicolons (multiple statements)
        if ";" in sql and not sql.strip().endswith(";"):
            return False, "Multiple SQL statements are not allowed"

        # Must have LIMIT clause
        if "LIMIT" not in sql_upper:
            return False, "LIMIT clause is required"

        return True, ""

    async def execute_safe(self, sql: str) -> list[dict]:
        """Execute SQL query safely

        Args:
            sql: SELECT query to execute

        Returns:
            List of result rows as dictionaries

        Raises:
            ValueError: If SQL is invalid or dangerous
            Exception: If query execution fails
        """
        # Validate first
        is_valid, error_msg = self.validate_sql(sql)
        if not is_valid:
            logger.warning(f"Invalid SQL query rejected: {error_msg}")
            raise ValueError(f"Invalid SQL: {error_msg}")

        # Execute query
        try:
            logger.info(f"Executing admin SQL query: {sql}")
            results = await self.db.fetchall(sql)
            logger.info(f"Query returned {len(results)} rows")
            return results
        except Exception as e:
            logger.error(f"SQL execution error: {e}", exc_info=True)
            raise Exception(f"Failed to execute query: {str(e)}")


