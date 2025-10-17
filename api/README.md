# Statistics API

Mock API для дашборда статистики Telegram бота.

## Быстрый старт

### Запуск API сервера

```bash
make api-run
```

Сервер будет доступен на `http://localhost:8000`

### Документация

Swagger UI: `http://localhost:8000/docs`
ReDoc: `http://localhost:8000/redoc`

### Остановка сервера

```bash
make api-stop
```

## Endpoints

### GET /stats

Получить статистику для дашборда.

**Query параметры:**
- `period` (optional): Период времени - `day`, `week`, или `month`. По умолчанию: `week`

**Response:**

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

### GET /health

Health check endpoint.

**Response:**

```json
{
  "status": "ok"
}
```

## Примеры запросов

### cURL

#### Получить статистику за неделю

```bash
curl http://localhost:8000/stats?period=week
```

#### Получить статистику за день

```bash
curl http://localhost:8000/stats?period=day
```

#### Получить статистику за месяц

```bash
curl http://localhost:8000/stats?period=month
```

#### Health check

```bash
curl http://localhost:8000/health
```

### PowerShell

#### Получить статистику за неделю

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/stats?period=week" -Method Get | ConvertTo-Json -Depth 10
```

#### Получить статистику за день

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/stats?period=day" -Method Get | ConvertTo-Json -Depth 10
```

#### Health check

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
```

### Python (requests)

```python
import requests

# Get statistics
response = requests.get("http://localhost:8000/stats", params={"period": "week"})
data = response.json()

print(f"KPI Metrics: {len(data['kpi_metrics'])}")
print(f"Timeline Points: {len(data['timeline'])}")

# Print metrics
for metric in data["kpi_metrics"]:
    print(f"{metric['label']}: {metric['value']} ({metric['trend']} {metric['change']}%)")
```

### JavaScript (fetch)

```javascript
// Get statistics
fetch('http://localhost:8000/stats?period=week')
  .then(response => response.json())
  .then(data => {
    console.log('KPI Metrics:', data.kpi_metrics);
    console.log('Timeline:', data.timeline);
  });
```

## Тестирование

### Запустить автоматические тесты

```bash
make test
```

### Быстрая проверка API

```bash
make api-test
```

## Архитектура

```
api/
├── __init__.py
├── api_main.py           # FastAPI application entrypoint
├── models.py             # Data models (KPIMetric, TimelinePoint, StatsResponse)
├── protocols.py          # StatCollectorProtocol interface
├── dependencies.py       # Dependency injection
├── collectors/
│   ├── __init__.py
│   ├── mock_collector.py # Mock implementation with test data
│   └── real_collector.py # Placeholder for real implementation
└── README.md
```

## Mock данные

Текущая реализация использует `MockStatCollector` который генерирует случайные, но реалистичные данные:

- **KPI метрики**: 4 метрики с форматированными значениями и трендами
- **Timeline**: Количество точек зависит от периода (day=24, week=7, month=30)
- **Тренды**: Автоматически определяются на основе процента изменения (>5% = up, <-5% = down, иначе stable)

## Замена на реальные данные

В будущем спринте (SP-FE-5) `MockStatCollector` будет заменен на `RealStatCollector`, который будет получать данные из базы данных SQLite.

Замена выполняется через dependency injection в `api/dependencies.py`:

```python
async def get_stat_collector() -> StatCollectorProtocol:
    # Заменить MockStatCollector на RealStatCollector
    return RealStatCollector(db_manager)
```

