"""Data models for API contracts"""

from dataclasses import dataclass
from enum import Enum


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

