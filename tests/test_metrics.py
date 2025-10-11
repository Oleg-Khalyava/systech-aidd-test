"""Тесты для системы метрик"""

import time

import pytest

from src.metrics import BotMetrics


@pytest.fixture
def metrics() -> BotMetrics:
    """Создает экземпляр метрик для тестов"""
    return BotMetrics()


def test_metrics_creation(metrics: BotMetrics) -> None:
    """Тест создания объекта метрик"""
    assert metrics.total_requests == 0
    assert metrics.total_errors == 0
    assert metrics.total_tokens == 0
    assert metrics.total_cost == 0.0
    assert len(metrics.active_users) == 0
    assert metrics.start_time > 0


def test_increment_requests(metrics: BotMetrics) -> None:
    """Тест увеличения счетчика запросов"""
    metrics.increment_requests()
    assert metrics.total_requests == 1

    metrics.increment_requests()
    assert metrics.total_requests == 2


def test_increment_errors(metrics: BotMetrics) -> None:
    """Тест увеличения счетчика ошибок"""
    metrics.increment_errors()
    assert metrics.total_errors == 1

    metrics.increment_errors()
    assert metrics.total_errors == 2


def test_add_tokens(metrics: BotMetrics) -> None:
    """Тест добавления токенов"""
    metrics.add_tokens(100)
    assert metrics.total_tokens == 100
    assert metrics.total_cost == 0.001  # 100 * 0.00001

    metrics.add_tokens(50)
    assert metrics.total_tokens == 150
    assert metrics.total_cost == pytest.approx(0.0015, rel=1e-6)


def test_add_tokens_custom_cost(metrics: BotMetrics) -> None:
    """Тест добавления токенов с кастомной стоимостью"""
    metrics.add_tokens(100, cost_per_token=0.00002)
    assert metrics.total_tokens == 100
    assert metrics.total_cost == 0.002


def test_add_active_user(metrics: BotMetrics) -> None:
    """Тест добавления активного пользователя"""
    metrics.add_active_user(123)
    assert 123 in metrics.active_users
    assert len(metrics.active_users) == 1

    metrics.add_active_user(456)
    assert len(metrics.active_users) == 2


def test_add_active_user_duplicate(metrics: BotMetrics) -> None:
    """Тест что дублирующиеся пользователи не добавляются дважды"""
    metrics.add_active_user(123)
    metrics.add_active_user(123)
    assert len(metrics.active_users) == 1


def test_get_uptime(metrics: BotMetrics) -> None:
    """Тест получения времени работы"""
    time.sleep(0.1)
    uptime = metrics.get_uptime()
    assert uptime >= 0.1
    assert uptime < 1.0


def test_get_uptime_formatted() -> None:
    """Тест форматированного времени работы"""
    # Создаем метрики с фиксированным временем запуска
    metrics = BotMetrics()
    metrics.start_time = time.time() - 90125  # 1д 1ч 2м 5с назад

    formatted = metrics.get_uptime_formatted()
    assert "1д" in formatted
    assert "1ч" in formatted
    assert "2м" in formatted
    assert "5с" in formatted


def test_get_error_rate_no_requests(metrics: BotMetrics) -> None:
    """Тест процента ошибок при нулевом количестве запросов"""
    assert metrics.get_error_rate() == 0.0


def test_get_error_rate(metrics: BotMetrics) -> None:
    """Тест расчета процента ошибок"""
    metrics.total_requests = 100
    metrics.total_errors = 5

    assert metrics.get_error_rate() == 5.0


def test_get_error_rate_all_errors(metrics: BotMetrics) -> None:
    """Тест процента ошибок при 100% ошибок"""
    metrics.total_requests = 10
    metrics.total_errors = 10

    assert metrics.get_error_rate() == 100.0


def test_get_stats(metrics: BotMetrics) -> None:
    """Тест получения статистики в виде словаря"""
    metrics.total_requests = 100
    metrics.total_errors = 5
    metrics.total_tokens = 1000
    metrics.total_cost = 0.01
    metrics.add_active_user(123)
    metrics.add_active_user(456)

    stats = metrics.get_stats()

    assert stats["total_requests"] == 100
    assert stats["total_errors"] == 5
    assert "5.00%" in stats["error_rate"]
    assert stats["total_tokens"] == 1000
    assert "$0.0100" in stats["total_cost"]
    assert stats["active_users"] == 2
    assert "uptime" in stats
    assert "start_time" in stats


def test_get_stats_formatted(metrics: BotMetrics) -> None:
    """Тест получения форматированной статистики"""
    metrics.total_requests = 100
    metrics.total_errors = 5

    formatted = metrics.get_stats_formatted()

    assert "Статистика бота" in formatted
    assert "100" in formatted  # requests
    assert "5" in formatted  # errors


def test_reset(metrics: BotMetrics) -> None:
    """Тест сброса метрик"""
    metrics.total_requests = 100
    metrics.total_errors = 5
    metrics.total_tokens = 1000
    metrics.total_cost = 0.01
    metrics.add_active_user(123)
    start_time = metrics.start_time

    metrics.reset()

    assert metrics.total_requests == 0
    assert metrics.total_errors == 0
    assert metrics.total_tokens == 0
    assert metrics.total_cost == 0.0
    assert len(metrics.active_users) == 0
    # start_time не должен сброситься
    assert metrics.start_time == start_time


def test_metrics_workflow(metrics: BotMetrics) -> None:
    """Тест полного рабочего процесса с метриками"""
    # Обработка нескольких запросов
    for i in range(10):
        metrics.increment_requests()
        metrics.add_active_user(i)
        metrics.add_tokens(50)

    # Пару ошибок
    metrics.increment_errors()
    metrics.increment_errors()

    # Проверяем итоговые значения
    assert metrics.total_requests == 10
    assert metrics.total_errors == 2
    assert metrics.get_error_rate() == 20.0
    assert metrics.total_tokens == 500
    assert len(metrics.active_users) == 10

    # Получаем статистику
    stats = metrics.get_stats()
    assert stats["total_requests"] == 10
    assert "20.00%" in stats["error_rate"]
