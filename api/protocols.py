"""Protocol definitions for statistics collectors"""

from typing import Protocol

from api.models import StatsResponse


class StatCollectorProtocol(Protocol):
    """Protocol for statistics collectors

    Defines interface for collecting statistics data.
    Implementations can be Mock (test data) or Real (from database).
    """

    async def get_stats(self, period: str) -> StatsResponse:
        """Get statistics for given period

        Args:
            period: Time period ("day", "week", "month")

        Returns:
            StatsResponse with KPI metrics and timeline data
        """
        ...

