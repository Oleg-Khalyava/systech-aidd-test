"""Mock implementation of statistics collector with test data"""

import random
from datetime import datetime, timedelta

from api.models import KPIMetric, StatsResponse, TimelinePoint, TrendEnum


class MockStatCollector:
    """Mock statistics collector with realistic test data

    Generates random but realistic statistics for testing and development.
    """

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

    def _format_number(self, value: int) -> str:
        """Format number with thousands separator

        Args:
            value: Integer value to format

        Returns:
            Formatted string like "1,234"
        """
        return f"{value:,}"

    def _generate_kpi_metrics(self) -> list[KPIMetric]:
        """Generate 4 KPI metrics with realistic test data

        Returns:
            List of 4 KPIMetric objects
        """
        # Total Users
        total_users = random.randint(1000, 2000)
        users_change = random.uniform(-15.0, 20.0)
        users_metric = KPIMetric(
            label="Total Users",
            value=self._format_number(total_users),
            change=round(users_change, 1),
            trend=self._determine_trend(users_change),
        )

        # Total Messages
        total_messages = random.randint(40000, 60000)
        messages_change = random.uniform(-10.0, 25.0)
        messages_metric = KPIMetric(
            label="Total Messages",
            value=self._format_number(total_messages),
            change=round(messages_change, 1),
            trend=self._determine_trend(messages_change),
        )

        # Deleted Messages
        deleted_messages = random.randint(800, 2000)
        deleted_change = random.uniform(-8.0, 5.0)  # Usually should be down
        deleted_metric = KPIMetric(
            label="Deleted Messages",
            value=self._format_number(deleted_messages),
            change=round(deleted_change, 1),
            trend=self._determine_trend(deleted_change),
        )

        # Average Message Length
        avg_length = random.randint(100, 200)
        length_change = random.uniform(-5.0, 10.0)
        length_metric = KPIMetric(
            label="Avg Message Length",
            value=f"{avg_length} chars",
            change=round(length_change, 1),
            trend=self._determine_trend(length_change),
        )

        return [users_metric, messages_metric, deleted_metric, length_metric]

    def _generate_timeline(self, period: str) -> list[TimelinePoint]:
        """Generate timeline data based on period

        Args:
            period: "day", "week", or "month"

        Returns:
            List of TimelinePoint objects
        """
        today = datetime.now()
        points: list[TimelinePoint] = []

        if period == "day":
            # 24 hours (hourly data)
            for hour in range(24):
                dt = today.replace(hour=hour, minute=0, second=0, microsecond=0)
                value = random.randint(20, 80)  # Messages per hour
                points.append(
                    TimelinePoint(
                        date=dt.strftime("%Y-%m-%dT%H:00:00"),
                        value=value,
                    )
                )
        elif period == "week":
            # 7 days (daily data)
            for day_offset in range(7):
                dt = today - timedelta(days=6 - day_offset)
                value = random.randint(400, 800)  # Messages per day
                points.append(
                    TimelinePoint(
                        date=dt.strftime("%Y-%m-%d"),
                        value=value,
                    )
                )
        else:  # month
            # 30 days (daily data)
            for day_offset in range(30):
                dt = today - timedelta(days=29 - day_offset)
                value = random.randint(400, 900)  # Messages per day
                points.append(
                    TimelinePoint(
                        date=dt.strftime("%Y-%m-%d"),
                        value=value,
                    )
                )

        return points

    async def get_stats(self, period: str) -> StatsResponse:
        """Get mock statistics for given period

        Args:
            period: Time period ("day", "week", "month")

        Returns:
            StatsResponse with generated test data
        """
        kpi_metrics = self._generate_kpi_metrics()
        timeline = self._generate_timeline(period)

        return StatsResponse(
            kpi_metrics=kpi_metrics,
            timeline=timeline,
        )
