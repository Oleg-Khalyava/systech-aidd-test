# 🚀 Quick Start: Statistics API

## Быстрый запуск за 3 шага

### 1. Установить зависимости

```bash
make install
```

### 2. Запустить API сервер

```bash
make api-run
```

Сервер запустится на `http://localhost:8000`

### 3. Открыть документацию

```bash
make api-docs
```

Или откройте в браузере: `http://localhost:8000/docs`

## Примеры использования

### Получить статистику за неделю

**cURL:**
```bash
curl http://localhost:8000/stats?period=week
```

**PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/stats?period=week" | ConvertTo-Json -Depth 10
```

**Python:**
```python
import requests
response = requests.get("http://localhost:8000/stats?period=week")
print(response.json())
```

### Периоды

- `day` - статистика за день (24 часа)
- `week` - статистика за неделю (7 дней) - **по умолчанию**
- `month` - статистика за месяц (30 дней)

## Структура ответа

```json
{
  "kpi_metrics": [
    {"label": "Total Users", "value": "1,234", "change": 12.5, "trend": "up"},
    {"label": "Total Messages", "value": "45,678", "change": 8.3, "trend": "up"},
    {"label": "Deleted Messages", "value": "1,250", "change": -5.2, "trend": "down"},
    {"label": "Avg Message Length", "value": "142 chars", "change": 2.1, "trend": "stable"}
  ],
  "timeline": [
    {"date": "2025-10-10", "value": 523},
    {"date": "2025-10-11", "value": 612}
  ]
}
```

## Доступные команды

```bash
make api-run      # Запустить API сервер
make api-stop     # Остановить API сервер
make api-test     # Протестировать API
make api-docs     # Открыть документацию
```

## Endpoints

- `GET /` - информация об API
- `GET /stats?period=week` - статистика дашборда
- `GET /health` - health check
- `GET /docs` - Swagger UI
- `GET /redoc` - ReDoc документация

## Тестирование

```bash
# Запустить все тесты API
uv run pytest tests/test_api.py -v

# Быстрый тест через Makefile
make api-test
```

## Swagger UI

После запуска `make api-run`, откройте:

**http://localhost:8000/docs**

Здесь вы можете:
- 📖 Просмотреть всю документацию API
- 🧪 Протестировать endpoints интерактивно
- 📊 Увидеть схемы данных
- 📝 Скопировать примеры запросов

## Troubleshooting

### API не запускается

```bash
# Проверьте, установлены ли зависимости
make install

# Проверьте, свободен ли порт 8000
netstat -an | findstr :8000
```

### Тесты не проходят

```bash
# Обновите зависимости
uv sync --all-extras

# Запустите тесты заново
uv run pytest tests/test_api.py -v
```

## Дополнительная документация

- [API README](api/README.md) - подробная документация API
- [Sprint Summary](docs/sprint_s1_summary.md) - итоги спринта S1
- [Plan](frontend/doc/frontend-roadmap.md) - roadmap и планы

## Следующие шаги

1. **Frontend разработчики**: используйте Mock API для разработки дашборда
2. **Backend разработчики**: подготовьтесь к реализации RealStatCollector в SP-FE-5
3. **QA инженеры**: тестируйте API через Swagger UI

---

**Mock API готов к использованию! 🎉**


