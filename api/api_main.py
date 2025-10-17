"""FastAPI application entrypoint for statistics dashboard API

This is a separate entrypoint from the main Telegram bot (src/main.py).
It provides REST API for frontend to fetch statistics data.

Run with: uvicorn api.api_main:app --reload --port 8000
API documentation: http://localhost:8000/docs
"""

from typing import Annotated

from fastapi import Depends, FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from api.chat_manager import ChatManager
from api.dependencies import get_chat_manager, get_stat_collector
from api.models import (
    ChatHistoryMessage,
    ChatHistoryResponse,
    ChatMode,
    ChatRequest,
    ChatResponse,
    PeriodEnum,
    StatsResponse,
)
from api.protocols import StatCollectorProtocol
from src.database.repository import DatabaseManager

# Create FastAPI application
app = FastAPI(
    title="Telegram Bot Statistics API",
    description="Mock API for dashboard statistics during frontend development",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint with API information

    Returns:
        Dict with welcome message and documentation link
    """
    return {
        "message": "Telegram Bot Statistics API",
        "documentation": "/docs",
        "version": "1.0.0",
    }


@app.get("/stats", response_model=StatsResponse)
async def get_stats(
    period: Annotated[str, Query(description="Time period for statistics")] = PeriodEnum.WEEK.value,
    collector: StatCollectorProtocol = Depends(get_stat_collector),  # noqa: B008
) -> StatsResponse:
    """Get statistics for dashboard

    Returns KPI metrics and timeline data for the specified period.

    Args:
        period: Time period - "day", "week", or "month" (default: "week")
        collector: Statistics collector (injected dependency)

    Returns:
        StatsResponse with:
        - kpi_metrics: 4 KPI cards (Total Users, Total Messages, Deleted Messages, Avg Length)
        - timeline: Timeline graph data points

    Example response:
    ```json
    {
        "kpi_metrics": [
            {
                "label": "Total Users",
                "value": "1,234",
                "change": 12.5,
                "trend": "up"
            },
            ...
        ],
        "timeline": [
            {"date": "2025-10-10", "value": 523},
            ...
        ]
    }
    ```
    """
    # Validate period parameter
    valid_periods = [p.value for p in PeriodEnum]
    if period not in valid_periods:
        period = PeriodEnum.WEEK.value

    # Get statistics from collector
    stats = await collector.get_stats(period)
    return stats


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint

    Returns:
        Dict with status "ok"
    """
    return {"status": "ok"}


@app.get("/api/chat/history/{user_id}", response_model=ChatHistoryResponse)
async def get_chat_history(
    user_id: int,
    limit: Annotated[int, Query(description="Maximum number of messages to return")] = 50,
    chat_manager: ChatManager = Depends(get_chat_manager),  # noqa: B008
) -> ChatHistoryResponse:
    """Get chat history for a user

    Returns recent messages ordered by created_at (oldest first for display).

    Args:
        user_id: User ID
        limit: Maximum number of messages to return (default: 50)
        chat_manager: Chat manager (injected dependency)

    Returns:
        ChatHistoryResponse with list of messages

    Example response:
    ```json
    {
        "messages": [
            {
                "id": 1,
                "role": "user",
                "content": "Hello!",
                "created_at": "2025-10-17T10:30:00"
            },
            {
                "id": 2,
                "role": "assistant",
                "content": "Hi! How can I help?",
                "created_at": "2025-10-17T10:30:05"
            }
        ]
    }
    ```
    """
    # Get recent messages from DB
    messages_data = await chat_manager.message_repo.get_recent(user_id, limit)

    # Convert to response model (reverse to show oldest first)
    messages = [
        ChatHistoryMessage(
            id=msg["id"],
            role=msg["role"],
            content=msg["content"],
            created_at=msg["created_at"],
        )
        for msg in reversed(messages_data)
    ]

    return ChatHistoryResponse(messages=messages)


@app.post("/api/chat/message", response_model=ChatResponse)
async def chat_message(
    request: ChatRequest,
    chat_manager: ChatManager = Depends(get_chat_manager),  # noqa: B008
) -> ChatResponse:
    """Send message to AI chat

    Supports two modes:
    - normal: Direct chat with LLM assistant
    - admin: Analytics mode with text-to-SQL queries

    Args:
        request: Chat request with message and mode
        chat_manager: Chat manager (injected dependency)

    Returns:
        ChatResponse with AI answer and optional SQL query

    Example request (normal mode):
    ```json
    {
        "message": "Hello, how are you?",
        "mode": "normal"
    }
    ```

    Example request (admin mode):
    ```json
    {
        "message": "Сколько всего пользователей?",
        "mode": "admin"
    }
    ```

    Example response (admin mode):
    ```json
    {
        "message": "В базе данных 1,234 активных пользователя",
        "sql": "SELECT COUNT(*) FROM users WHERE deleted_at IS NULL"
    }
    ```
    """
    if request.mode == ChatMode.NORMAL:
        # Normal mode - direct LLM chat
        answer = await chat_manager.handle_normal(request.user_id, request.message)
        return ChatResponse(message=answer, sql=None)
    else:
        # Admin mode - text-to-SQL analytics
        answer, sql = await chat_manager.handle_admin(request.user_id, request.message)
        return ChatResponse(message=answer, sql=sql)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
