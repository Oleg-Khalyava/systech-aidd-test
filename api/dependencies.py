"""Dependency injection for FastAPI"""

from api.collectors.mock_collector import MockStatCollector
from api.protocols import StatCollectorProtocol


async def get_stat_collector() -> StatCollectorProtocol:
    """Get statistics collector instance

    Currently returns MockStatCollector for development.
    In SP-FE-5, this will be replaced with RealStatCollector.

    Returns:
        StatCollectorProtocol implementation
    """
    return MockStatCollector()

