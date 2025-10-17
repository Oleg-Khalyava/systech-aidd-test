<!-- 25be2357-2ce0-43d6-8b00-a7b76f137079 c12ace7b-882d-4d31-abbc-ddf947a28843 -->
# Sprint 1 (S1): Mock API для дашборда статистики

## Архитектура и структура

### Новые файлы и директории

- `api/` - новая директория для API
  - `__init__.py`
  - `api_main.py` - entrypoint для FastAPI приложения
  - `models.py` - dataclasses для API контрактов (request/response)
  - `protocols.py` - протокол `StatCollectorProtocol`
  - `collectors/` - реализации сборщиков статистики
    - `__init__.py`
    - `mock_collector.py` - `MockStatCollector` с тестовыми данными
    - `real_collector.py` - заглушка для будущей реализации
  - `dependencies.py` - dependency injection для FastAPI

### Обновляемые файлы

- `pyproject.toml` - добавить FastAPI, uvicorn, pydantic
- `Makefile` - добавить команды `api-run`, `api-test`, `api-docs`

## API Контракт

### Endpoint: GET /stats

**Query параметры:**

- `period`: str = "week" (enum: "day" | "week" | "month")

**Response структура:**

```python
@dataclass
class KPIMetric:
    label: str          # "Total Users"
    value: str          # "1,250" (форматированное значение)
    change: float       # 12.5 (процент изменения, может быть отрицательным)
    trend: str          # "up" | "down" | "stable"

@dataclass
class TimelinePoint:
    date: str           # "2025-10-17" (дата в ISO формате)
    value: int          # количество сообщений

@dataclass
class StatsResponse:
    kpi_metrics: list[KPIMetric]        # 4 KPI карточки
    timeline: list[TimelinePoint]        # данные для графика активности
```

## Маппинг метрик дашборда → статистика бота

**4 основные KPI карточки:**

1. **Total Users** → Общее количество пользователей (всего в БД)
2. **Total Messages** → Общее количество сообщений (всего в БД)
3. **Deleted Messages** → Количество удаленных сообщений (soft delete, deleted_at IS NOT NULL)
4. **Average Message Length** → Средняя длина сообщений (AVG(length))

**График:**

5. **Timeline Graph** → активность сообщений по времени (дням/неделям/месяцам)

## Mock данные

`MockStatCollector` генерирует реалистичные данные:

- Случайные значения в правдоподобных диапазонах для 4 KPI метрик
- Тренды (рост/падение/стабильность) с логичными процентами изменения
- Timeline данные с количеством точек в зависимости от периода

### Пример JSON response (GET /stats?period=week):

```json
{
  "kpi_metrics": [
    {
      "label": "Total Users",
      "value": "1,234",
      "change": 12.5,
      "trend": "up"
    },
    {
      "label": "Total Messages",
      "value": "45,678",
      "change": 8.3,
      "trend": "up"
    },
    {
      "label": "Deleted Messages",
      "value": "1,250",
      "change": -5.2,
      "trend": "down"
    },
    {
      "label": "Avg Message Length",
      "value": "142 chars",
      "change": 2.1,
      "trend": "stable"
    }
  ],
  "timeline": [
    {"date": "2025-10-10", "value": 523},
    {"date": "2025-10-11", "value": 612},
    {"date": "2025-10-12", "value": 580},
    {"date": "2025-10-13", "value": 695},
    {"date": "2025-10-14", "value": 701},
    {"date": "2025-10-15", "value": 643},
    {"date": "2025-10-16", "value": 720}
  ]
}
```

**Особенности генерации:**

- `kpi_metrics[].value` - форматируется с запятыми/единицами для читаемости ("1,234", "142 chars")
- `kpi_metrics[].change` - процент изменения относительно предыдущего периода (положительный/отрицательный)
- `kpi_metrics[].trend` - определяется автоматически: "up" (>5%), "down" (<-5%), "stable" (±5%)
- `timeline` - количество точек зависит от `period`: day=24 (часы), week=7 (дни), month=30 (дни)

## Технические детали

### FastAPI настройки

- Автоматическая генерация OpenAPI/Swagger документации
- CORS middleware для локальной разработки
- Pydantic модели для валидации
- Dependency injection для подмены Mock/Real collector

### Запуск API

```bash
make api-run    # uvicorn api.api_main:app --reload --port 8000
make api-test   # curl тест GET /stats?period=week
make api-docs   # открыть http://localhost:8000/docs
```

### Структура кода

- Использовать Protocol для `StatCollectorProtocol`
- Dependency injection через FastAPI `Depends()`
- Mock collector возвращает фиксированные + случайные данные
- Вся бизнес-логика изолирована в collectors

## Дополнительные требования

1. Документация API автоматически доступна на `/docs` (Swagger UI)
2. Все response модели валидируются через Pydantic/dataclasses
3. Код соответствует существующим стандартам (black, ruff, mypy)
4. API независим от основного Telegram бота (отдельный entrypoint)
5. Контракт API задокументирован в виде примеров JSON в комментариях

## Результаты спринта

После завершения:

- FastAPI сервер запускается на порту 8000
- GET `/stats?period=day|week|month` возвращает структурированные данные
- Swagger UI доступен на `/docs`
- Frontend разработчики могут начать работу с Mock API
- Подготовлена архитектура для замены Mock → Real collector

### To-dos

- [ ] Добавить FastAPI, uvicorn, pydantic в pyproject.toml
- [ ] Создать директорию api/ и базовую структуру файлов
- [ ] Реализовать StatCollectorProtocol в api/protocols.py
- [ ] Создать dataclasses для API контракта в api/models.py (KPIMetric, TimelinePoint, Conversation, TopUser, StatsResponse)
- [ ] Реализовать MockStatCollector с генерацией реалистичных тестовых данных
- [ ] Создать FastAPI приложение в api/api_main.py с endpoint GET /stats и dependency injection
- [ ] Добавить команды api-run, api-test, api-docs в Makefile
- [ ] Создать тесты для API endpoint и MockStatCollector