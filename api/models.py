"""Data models for API contracts"""

from dataclasses import dataclass
from enum import Enum

from pydantic import BaseModel


class PeriodEnum(str, Enum):
    """Time period for statistics"""

    DAY = "day"
    WEEK = "week"
    MONTH = "month"


class TrendEnum(str, Enum):
    """Trend direction for metrics"""

    UP = "up"
    DOWN = "down"
    STABLE = "stable"


@dataclass
class KPIMetric:
    """KPI metric for dashboard card

    Example JSON:
    {
        "label": "Total Users",
        "value": "1,234",
        "change": 12.5,
        "trend": "up"
    }
    """

    label: str  # Metric label, e.g. "Total Users"
    value: str  # Formatted value, e.g. "1,234" or "142 chars"
    change: float  # Percent change from previous period (can be negative)
    trend: str  # "up", "down", or "stable"


@dataclass
class TimelinePoint:
    """Single point in timeline graph

    Example JSON:
    {
        "date": "2025-10-17",
        "value": 523
    }
    """

    date: str  # Date in ISO format (YYYY-MM-DD)
    value: int  # Number of messages


@dataclass
class StatsResponse:
    """Complete statistics response

    Example JSON:
    {
        "kpi_metrics": [...],
        "timeline": [...]
    }
    """

    kpi_metrics: list[KPIMetric]  # 4 KPI dashboard cards
    timeline: list[TimelinePoint]  # Timeline graph data


# Chat API Models


class ChatMode(str, Enum):
    """Chat mode for AI assistant"""

    NORMAL = "normal"  # Normal chat with LLM
    ADMIN = "admin"  # Admin mode with text-to-SQL analytics


class ChatRequest(BaseModel):
    """Request to send message to chat

    Example JSON:
    {
        "user_id": 123,
        "message": "Hello, how are you?",
        "mode": "normal"
    }
    """

    user_id: int  # User ID for tracking messages in DB (can be any unique identifier for web users)
    message: str
    mode: ChatMode = ChatMode.NORMAL


class ChatResponse(BaseModel):
    """Response from chat API

    Example JSON:
    {
        "message": "I'm doing well, thank you!",
        "sql": null
    }
    """

    message: str
    sql: str | None = None


class ChatHistoryMessage(BaseModel):
    """Single message in chat history

    Example JSON:
    {
        "id": 123,
        "role": "user",
        "content": "Hello!",
        "created_at": "2025-10-17T10:30:00"
    }
    """

    id: int
    role: str  # "user" or "assistant"
    content: str
    created_at: str


class ChatHistoryResponse(BaseModel):
    """Response with chat history

    Example JSON:
    {
        "messages": [...]
    }
    """

    messages: list[ChatHistoryMessage]
