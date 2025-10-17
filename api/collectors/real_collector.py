"""Real implementation of statistics collector (placeholder for future)"""

from api.models import StatsResponse


class RealStatCollector:
    """Real statistics collector using database

    TODO: Implement in SP-FE-5 when replacing Mock with Real data.
    This will query the actual SQLite database to get real statistics.
    """

    async def get_stats(self, period: str) -> StatsResponse:
        """Get real statistics from database

        Args:
            period: Time period ("day", "week", "month")

        Returns:
            StatsResponse with real data from database
        """
        raise NotImplementedError("Real collector not implemented yet. Use MockStatCollector.")

