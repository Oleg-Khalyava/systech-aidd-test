"""FastAPI application entrypoint for statistics dashboard API

This is a separate entrypoint from the main Telegram bot (src/main.py).
It provides REST API for frontend to fetch statistics data.

Run with: uvicorn api.api_main:app --reload --port 8000
API documentation: http://localhost:8000/docs
"""

from typing import Annotated

from fastapi import Depends, FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from api.dependencies import get_stat_collector
from api.models import PeriodEnum, StatsResponse
from api.protocols import StatCollectorProtocol

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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
