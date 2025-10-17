"""Tests for API endpoints and statistics collectors"""

import pytest
from fastapi.testclient import TestClient

from api.api_main import app
from api.collectors.mock_collector import MockStatCollector
from api.models import PeriodEnum

# Create test client
client = TestClient(app)


class TestAPIEndpoints:
    """Test API endpoints"""

    def test_root_endpoint(self) -> None:
        """Test root endpoint returns API information"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "documentation" in data
        assert "version" in data

    def test_health_check(self) -> None:
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_stats_endpoint_default_period(self) -> None:
        """Test stats endpoint with default period (week)"""
        response = client.get("/stats")
        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert "kpi_metrics" in data
        assert "timeline" in data

        # Check KPI metrics
        assert len(data["kpi_metrics"]) == 4
        for metric in data["kpi_metrics"]:
            assert "label" in metric
            assert "value" in metric
            assert "change" in metric
            assert "trend" in metric

        # Check timeline
        assert len(data["timeline"]) == 7  # week has 7 days
        for point in data["timeline"]:
            assert "date" in point
            assert "value" in point

    def test_stats_endpoint_day_period(self) -> None:
        """Test stats endpoint with day period"""
        response = client.get("/stats?period=day")
        assert response.status_code == 200
        data = response.json()

        # Check timeline has 24 points (hourly)
        assert len(data["timeline"]) == 24

    def test_stats_endpoint_week_period(self) -> None:
        """Test stats endpoint with week period"""
        response = client.get("/stats?period=week")
        assert response.status_code == 200
        data = response.json()

        # Check timeline has 7 points (daily)
        assert len(data["timeline"]) == 7

    def test_stats_endpoint_month_period(self) -> None:
        """Test stats endpoint with month period"""
        response = client.get("/stats?period=month")
        assert response.status_code == 200
        data = response.json()

        # Check timeline has 30 points (daily)
        assert len(data["timeline"]) == 30

    def test_stats_endpoint_invalid_period(self) -> None:
        """Test stats endpoint with invalid period defaults to week"""
        response = client.get("/stats?period=invalid")
        assert response.status_code == 200
        data = response.json()

        # Should default to week (7 days)
        assert len(data["timeline"]) == 7

    def test_kpi_metrics_labels(self) -> None:
        """Test that KPI metrics have correct labels"""
        response = client.get("/stats")
        assert response.status_code == 200
        data = response.json()

        labels = [metric["label"] for metric in data["kpi_metrics"]]
        assert "Total Users" in labels
        assert "Total Messages" in labels
        assert "Deleted Messages" in labels
        assert "Avg Message Length" in labels

    def test_kpi_metrics_trends(self) -> None:
        """Test that KPI metrics have valid trend values"""
        response = client.get("/stats")
        assert response.status_code == 200
        data = response.json()

        valid_trends = ["up", "down", "stable"]
        for metric in data["kpi_metrics"]:
            assert metric["trend"] in valid_trends


class TestMockStatCollector:
    """Test MockStatCollector"""

    @pytest.mark.asyncio
    async def test_get_stats_returns_correct_structure(self) -> None:
        """Test that get_stats returns correct data structure"""
        collector = MockStatCollector()
        stats = await collector.get_stats("week")

        assert stats.kpi_metrics is not None
        assert stats.timeline is not None
        assert len(stats.kpi_metrics) == 4
        assert len(stats.timeline) > 0

    @pytest.mark.asyncio
    async def test_get_stats_day_period(self) -> None:
        """Test get_stats with day period"""
        collector = MockStatCollector()
        stats = await collector.get_stats(PeriodEnum.DAY.value)

        # Day period should have 24 timeline points (hourly)
        assert len(stats.timeline) == 24

    @pytest.mark.asyncio
    async def test_get_stats_week_period(self) -> None:
        """Test get_stats with week period"""
        collector = MockStatCollector()
        stats = await collector.get_stats(PeriodEnum.WEEK.value)

        # Week period should have 7 timeline points (daily)
        assert len(stats.timeline) == 7

    @pytest.mark.asyncio
    async def test_get_stats_month_period(self) -> None:
        """Test get_stats with month period"""
        collector = MockStatCollector()
        stats = await collector.get_stats(PeriodEnum.MONTH.value)

        # Month period should have 30 timeline points (daily)
        assert len(stats.timeline) == 30

    @pytest.mark.asyncio
    async def test_kpi_metrics_format(self) -> None:
        """Test that KPI metrics are formatted correctly"""
        collector = MockStatCollector()
        stats = await collector.get_stats("week")

        for metric in stats.kpi_metrics:
            # Check that label is not empty
            assert len(metric.label) > 0

            # Check that value is not empty
            assert len(metric.value) > 0

            # Check that change is a valid float
            assert isinstance(metric.change, float)

            # Check that trend is valid
            assert metric.trend in ["up", "down", "stable"]

    @pytest.mark.asyncio
    async def test_timeline_format(self) -> None:
        """Test that timeline data is formatted correctly"""
        collector = MockStatCollector()
        stats = await collector.get_stats("week")

        for point in stats.timeline:
            # Check that date is not empty
            assert len(point.date) > 0

            # Check that value is a positive integer
            assert isinstance(point.value, int)
            assert point.value > 0

    @pytest.mark.asyncio
    async def test_trend_determination(self) -> None:
        """Test trend determination logic"""
        collector = MockStatCollector()

        # Test trend logic directly
        assert collector._determine_trend(10.0) == "up"
        assert collector._determine_trend(-10.0) == "down"
        assert collector._determine_trend(2.0) == "stable"
        assert collector._determine_trend(-2.0) == "stable"
        assert collector._determine_trend(0.0) == "stable"

    @pytest.mark.asyncio
    async def test_number_formatting(self) -> None:
        """Test number formatting with thousands separator"""
        collector = MockStatCollector()

        assert collector._format_number(1234) == "1,234"
        assert collector._format_number(1234567) == "1,234,567"
        assert collector._format_number(999) == "999"
        assert collector._format_number(1000) == "1,000"

