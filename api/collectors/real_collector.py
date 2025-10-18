"""Real implementation of statistics collector with database queries"""

import logging
from datetime import datetime, timedelta

from api.models import KPIMetric, StatsResponse, TimelinePoint, TrendEnum
from src.database.repository import DatabaseManager

logger = logging.getLogger("telegram_bot")


class RealStatCollector:
    """Real statistics collector with database queries

    Fetches actual statistics from SQLite database.
    """

    def __init__(self, db_manager: DatabaseManager):
        """Initialize collector with database manager

        Args:
            db_manager: Database manager instance
        """
        self.db = db_manager

    def _determine_trend(self, change: float) -> str:
        """Determine trend based on change percentage

        Args:
            change: Percent change value

        Returns:
            Trend string: "up" (>5%), "down" (<-5%), or "stable" (±5%)
        """
        if change > 5.0:
            return TrendEnum.UP.value
        elif change < -5.0:
            return TrendEnum.DOWN.value
        else:
            return TrendEnum.STABLE.value

    def _format_number(self, value: int | float) -> str:
        """Format number with thousands separator

        Args:
            value: Number to format

        Returns:
            Formatted string like "1,234"
        """
        return f"{int(value):,}"

    def _get_period_dates(self, period: str) -> tuple[str, str, str, str]:
        """Calculate date ranges for current and previous periods

        Args:
            period: "day", "week", or "month"

        Returns:
            Tuple of (current_start, current_end, previous_start, previous_end)
        """
        now = datetime.now()

        if period == "day":
            # Current: today, Previous: yesterday
            current_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            current_end = now
            previous_start = current_start - timedelta(days=1)
            previous_end = current_start
        elif period == "week":
            # Current: last 7 days, Previous: 7 days before that
            current_start = now - timedelta(days=7)
            current_end = now
            previous_start = current_start - timedelta(days=7)
            previous_end = current_start
        else:  # month
            # Current: last 30 days, Previous: 30 days before that
            current_start = now - timedelta(days=30)
            current_end = now
            previous_start = current_start - timedelta(days=30)
            previous_end = current_start

        return (
            current_start.isoformat(),
            current_end.isoformat(),
            previous_start.isoformat(),
            previous_end.isoformat(),
        )

    async def _get_metric_with_change(
        self, label: str, current_query: str, previous_query: str, format_value: callable
    ) -> KPIMetric:
        """Get metric with calculated change percentage

        Args:
            label: Metric label
            current_query: SQL query for current period
            previous_query: SQL query for previous period
            format_value: Function to format the value

        Returns:
            KPIMetric with value, change, and trend
        """
        # Get current value
        current_result = await self.db.fetchone(current_query)
        current_value = (
            list(current_result.values())[0] if current_result else 0
        )

        # Get previous value
        previous_result = await self.db.fetchone(previous_query)
        previous_value = (
            list(previous_result.values())[0] if previous_result else 0
        )

        # Calculate change percentage
        if previous_value and previous_value > 0:
            change = ((current_value - previous_value) / previous_value) * 100
        else:
            change = 0.0

        return KPIMetric(
            label=label,
            value=format_value(current_value),
            change=round(change, 1),
            trend=self._determine_trend(change),
        )

    async def _generate_kpi_metrics(self, period: str) -> list[KPIMetric]:
        """Generate 4 KPI metrics with real data from database

        Args:
            period: Time period ("day", "week", "month")

        Returns:
            List of 4 KPIMetric objects
        """
        current_start, current_end, previous_start, previous_end = (
            self._get_period_dates(period)
        )

        # Total Users (active users) - all time count
        total_users = await self.db.fetchone(
            "SELECT COUNT(*) as count FROM users WHERE deleted_at IS NULL"
        )
        users_count = total_users["count"] if total_users else 0

        # Total Messages (in current period)
        total_messages_current = await self.db.fetchone(
            """
            SELECT COUNT(*) as count FROM messages
            WHERE deleted_at IS NULL
            AND created_at >= ? AND created_at <= ?
            """,
            (current_start, current_end),
        )
        messages_current = (
            total_messages_current["count"] if total_messages_current else 0
        )

        total_messages_previous = await self.db.fetchone(
            """
            SELECT COUNT(*) as count FROM messages
            WHERE deleted_at IS NULL
            AND created_at >= ? AND created_at < ?
            """,
            (previous_start, previous_end),
        )
        messages_previous = (
            total_messages_previous["count"] if total_messages_previous else 0
        )

        if messages_previous > 0:
            messages_change = (
                (messages_current - messages_previous) / messages_previous
            ) * 100
        else:
            messages_change = 0.0

        messages_metric = KPIMetric(
            label="Total Messages",
            value=self._format_number(messages_current),
            change=round(messages_change, 1),
            trend=self._determine_trend(messages_change),
        )

        # Deleted Messages (all time)
        deleted_current = await self.db.fetchone(
            """
            SELECT COUNT(*) as count FROM messages
            WHERE deleted_at IS NOT NULL
            AND deleted_at >= ? AND deleted_at <= ?
            """,
            (current_start, current_end),
        )
        deleted_count_current = deleted_current["count"] if deleted_current else 0

        deleted_previous = await self.db.fetchone(
            """
            SELECT COUNT(*) as count FROM messages
            WHERE deleted_at IS NOT NULL
            AND deleted_at >= ? AND deleted_at < ?
            """,
            (previous_start, previous_end),
        )
        deleted_count_previous = (
            deleted_previous["count"] if deleted_previous else 0
        )

        if deleted_count_previous > 0:
            deleted_change = (
                (deleted_count_current - deleted_count_previous)
                / deleted_count_previous
            ) * 100
        else:
            deleted_change = 0.0

        deleted_metric = KPIMetric(
            label="Deleted Messages",
            value=self._format_number(deleted_count_current),
            change=round(deleted_change, 1),
            trend=self._determine_trend(deleted_change),
        )

        # Average Message Length (in current period)
        avg_length_current = await self.db.fetchone(
            """
            SELECT AVG(length) as avg_length FROM messages
            WHERE deleted_at IS NULL
            AND created_at >= ? AND created_at <= ?
            """,
            (current_start, current_end),
        )
        avg_current = (
            avg_length_current["avg_length"]
            if avg_length_current and avg_length_current["avg_length"] is not None
            else 0
        )

        avg_length_previous = await self.db.fetchone(
            """
            SELECT AVG(length) as avg_length FROM messages
            WHERE deleted_at IS NULL
            AND created_at >= ? AND created_at < ?
            """,
            (previous_start, previous_end),
        )
        avg_previous = (
            avg_length_previous["avg_length"]
            if avg_length_previous and avg_length_previous["avg_length"] is not None
            else 0
        )

        if avg_previous and avg_previous > 0:
            avg_change = ((avg_current - avg_previous) / avg_previous) * 100
        else:
            avg_change = 0.0

        avg_metric = KPIMetric(
            label="Avg Message Length",
            value=f"{int(avg_current)} chars" if avg_current else "0 chars",
            change=round(avg_change, 1),
            trend=self._determine_trend(avg_change),
        )

        # Use total users count for first metric
        users_metric_final = KPIMetric(
            label="Total Users",
            value=self._format_number(users_count),
            change=0.0,  # We don't track user change over time periods
            trend="stable",
        )

        return [users_metric_final, messages_metric, deleted_metric, avg_metric]

    async def _generate_timeline(self, period: str) -> list[TimelinePoint]:
        """Generate timeline data based on period with real database data

        Args:
            period: "day", "week", or "month"

        Returns:
            List of TimelinePoint objects
        """
        now = datetime.now()
        points: list[TimelinePoint] = []

        if period == "day":
            # 24 hours (hourly data)
            for hour in range(24):
                start_time = now.replace(
                    hour=hour, minute=0, second=0, microsecond=0
                )
                end_time = start_time + timedelta(hours=1)

                result = await self.db.fetchone(
                    """
                    SELECT COUNT(*) as count FROM messages
                    WHERE deleted_at IS NULL
                    AND created_at >= ? AND created_at < ?
                    """,
                    (start_time.isoformat(), end_time.isoformat()),
                )
                count = result["count"] if result else 0

                points.append(
                    TimelinePoint(
                        date=start_time.strftime("%Y-%m-%dT%H:00:00"), value=count
                    )
                )
        elif period == "week":
            # 7 days (daily data)
            for day_offset in range(7):
                day = now - timedelta(days=6 - day_offset)
                start_time = day.replace(hour=0, minute=0, second=0, microsecond=0)
                end_time = start_time + timedelta(days=1)

                result = await self.db.fetchone(
                    """
                    SELECT COUNT(*) as count FROM messages
                    WHERE deleted_at IS NULL
                    AND created_at >= ? AND created_at < ?
                    """,
                    (start_time.isoformat(), end_time.isoformat()),
                )
                count = result["count"] if result else 0

                points.append(
                    TimelinePoint(date=start_time.strftime("%Y-%m-%d"), value=count)
                )
        else:  # month
            # 30 days (daily data)
            for day_offset in range(30):
                day = now - timedelta(days=29 - day_offset)
                start_time = day.replace(hour=0, minute=0, second=0, microsecond=0)
                end_time = start_time + timedelta(days=1)

                result = await self.db.fetchone(
                    """
                    SELECT COUNT(*) as count FROM messages
                    WHERE deleted_at IS NULL
                    AND created_at >= ? AND created_at < ?
                    """,
                    (start_time.isoformat(), end_time.isoformat()),
                )
                count = result["count"] if result else 0

                points.append(
                    TimelinePoint(date=start_time.strftime("%Y-%m-%d"), value=count)
                )

        return points

    async def get_stats(self, period: str) -> StatsResponse:
        """Get real statistics from database for given period

        Args:
            period: Time period ("day", "week", "month")

        Returns:
            StatsResponse with real data from database
        """
        logger.info(f"Fetching real statistics for period: {period}")

        kpi_metrics = await self._generate_kpi_metrics(period)
        timeline = await self._generate_timeline(period)

        logger.info(
            f"Generated {len(kpi_metrics)} KPI metrics and {len(timeline)} timeline points"
        )

        return StatsResponse(
            kpi_metrics=kpi_metrics,
            timeline=timeline,
        )
