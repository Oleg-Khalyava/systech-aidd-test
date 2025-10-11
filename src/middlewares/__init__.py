"""Middlewares для Telegram бота"""

from src.middlewares.dependency_injection import DependencyInjectionMiddleware
from src.middlewares.rate_limit import RateLimitMiddleware

__all__ = ["RateLimitMiddleware", "DependencyInjectionMiddleware"]
