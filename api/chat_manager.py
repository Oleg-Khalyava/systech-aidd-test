"""Chat manager for handling AI chat requests in normal and admin modes"""

import json
import logging
from pathlib import Path

from api.sql_executor import SQLExecutor
from llm.client import LLMClient
from src.database.repository import DatabaseManager, MessageRepository, UserRepository

logger = logging.getLogger("telegram_bot")


class ChatManager:
    """Manage chat interactions with AI in different modes

    Supports two modes:
    - normal: Direct chat with LLM
    - admin: Analytics mode with text-to-SQL pipeline
    """

    def __init__(self, llm_client: LLMClient, db_manager: DatabaseManager):
        """Initialize chat manager

        Args:
            llm_client: LLM client for AI interactions
            db_manager: Database manager for admin mode queries
        """
        self.llm = llm_client
        self.db = db_manager
        self.sql_executor = SQLExecutor(db_manager)
        self.message_repo = MessageRepository(db_manager)
        self.user_repo = UserRepository(db_manager)

        # Load text-to-SQL prompt
        prompt_path = Path("prompts/text2sql.txt")
        if prompt_path.exists():
            self.text2sql_prompt = prompt_path.read_text(encoding="utf-8")
        else:
            logger.warning("text2sql.txt not found, admin mode may not work properly")
            self.text2sql_prompt = "Convert the following question to SQL:"

    async def handle_normal(self, user_id: int, message: str) -> str:
        """Handle normal chat mode - direct LLM interaction

        Args:
            user_id: User ID for tracking messages
            message: User's message

        Returns:
            AI response text
        """
        logger.info(f"Handling normal mode chat request for user {user_id}")

        # Ensure user exists in DB (create if needed with generic name)
        await self.user_repo.get_or_create(
            chat_id=user_id,
            username=None,
            first_name=f"WebUser_{user_id}"
        )

        # Save user message to DB
        await self.message_repo.create(
            user_id=user_id,
            role="user",
            content=message
        )

        # Simple system prompt for general assistant
        messages = [
            {
                "role": "system",
                "content": "Ты полезный AI-ассистент. Отвечай дружелюбно и информативно на русском языке.",
            },
            {"role": "user", "content": message},
        ]

        # Get response from LLM
        response = await self.llm.send_message(messages)

        # Save assistant response to DB
        await self.message_repo.create(
            user_id=user_id,
            role="assistant",
            content=response
        )

        return response

    async def handle_admin(self, user_id: int, message: str) -> tuple[str, str]:
        """Handle admin mode - text-to-SQL analytics pipeline

        Pipeline:
        1. Convert user question to SQL using LLM
        2. Validate and execute SQL query
        3. Format results and generate natural language answer

        Args:
            user_id: User ID for tracking messages
            message: User's analytics question

        Returns:
            Tuple of (answer_text, sql_query)

        Raises:
            Exception: If any step in the pipeline fails
        """
        logger.info(f"Handling admin mode chat request for user {user_id}")

        # Ensure user exists in DB (create if needed with generic name)
        await self.user_repo.get_or_create(
            chat_id=user_id,
            username=None,
            first_name=f"WebUser_{user_id}"
        )

        # Save user message to DB
        await self.message_repo.create(
            user_id=user_id,
            role="user",
            content=message
        )

        # Step 1: Convert question to SQL
        sql_query = await self._question_to_sql(message)
        logger.info(f"Generated SQL: {sql_query}")

        # Step 2: Execute SQL query
        try:
            results = await self.sql_executor.execute_safe(sql_query)
        except Exception as e:
            error_msg = f"Ошибка выполнения SQL: {str(e)}"
            logger.error(error_msg)
            # Save error message to DB
            await self.message_repo.create(
                user_id=user_id,
                role="assistant",
                content=error_msg
            )
            return error_msg, sql_query

        # Step 3: Generate natural language answer from results
        answer = await self._results_to_answer(message, sql_query, results)

        # Save assistant response to DB
        await self.message_repo.create(
            user_id=user_id,
            role="assistant",
            content=answer
        )

        return answer, sql_query

    async def _question_to_sql(self, question: str) -> str:
        """Convert natural language question to SQL query

        Args:
            question: User's question in natural language

        Returns:
            SQL query string
        """
        # Prepare prompt with question
        full_prompt = f"{self.text2sql_prompt}\n\n{question}"

        messages = [{"role": "user", "content": full_prompt}]

        # Get SQL from LLM
        response = await self.llm.send_message(messages)

        # Clean up response (remove markdown, extra whitespace)
        sql = response.strip()
        sql = sql.replace("```sql", "").replace("```", "")
        sql = sql.strip()

        return sql

    async def _results_to_answer(
        self, question: str, sql: str, results: list[dict]
    ) -> str:
        """Convert SQL results to natural language answer

        Args:
            question: Original user question
            sql: SQL query that was executed
            results: Query results

        Returns:
            Natural language answer
        """
        # Format results for LLM
        if not results:
            return "Запрос выполнен успешно, но не вернул результатов."

        # Limit results shown to LLM to avoid token limits
        results_to_show = results[:50]  # Max 50 rows
        results_str = json.dumps(results_to_show, ensure_ascii=False, indent=2)

        prompt = f"""На основе следующих данных из базы данных, ответь на вопрос пользователя.

Вопрос пользователя: {question}

SQL запрос: {sql}

Результаты запроса:
{results_str}

Всего строк: {len(results)}

Сформулируй понятный и информативный ответ на русском языке. Если результатов много, обобщи их.
Не упоминай SQL запрос в ответе, только данные."""

        messages = [{"role": "user", "content": prompt}]

        response = await self.llm.send_message(messages)
        return response

