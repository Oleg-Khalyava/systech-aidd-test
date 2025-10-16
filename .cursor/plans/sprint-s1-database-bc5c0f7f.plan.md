<!-- bc5c0f7f-676b-419a-8591-eb6ea6b789a7 d5b595d6-dc0d-4096-a71e-644674881870 -->
# Sprint S1: База данных для персистентного хранения

## Принципы

- **KISS**: SQLite + aiosqlite, прямой SQL без ORM, никаких лишних абстракций
- **Soft delete**: физически не удаляем (поля `deleted_at`)
- **Метаданные**: каждое сообщение имеет `created_at` и `length` (в символах)

## Технологии

- **БД**: SQLite с FTS5 для полнотекстового поиска
- **Async**: aiosqlite
- **Миграции**: Alembic
- **Паттерн**: Repository (без Protocol - KISS)

## Схема БД

### Таблица `users`

```sql
- id: INTEGER PRIMARY KEY           -- chat_id из Telegram
- username: TEXT NULL
- first_name: TEXT NOT NULL
- current_role: TEXT NOT NULL        -- текущая роль/промпт пользователя
- created_at: TIMESTAMP NOT NULL
- last_accessed: TIMESTAMP NOT NULL
- deleted_at: TIMESTAMP NULL         -- soft delete
```

### Таблица `messages`

```sql
- id: INTEGER PRIMARY KEY AUTOINCREMENT
- user_id: INTEGER NOT NULL
- role: TEXT NOT NULL                -- 'user', 'assistant', 'system'
- content: TEXT NOT NULL
- length: INTEGER NOT NULL           -- len(content) для аналитики
- created_at: TIMESTAMP NOT NULL
- deleted_at: TIMESTAMP NULL         -- soft delete
- FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
- INDEX: (user_id, created_at)
```

### FTS5 таблица `messages_fts`

```sql
- Виртуальная таблица для полнотекстового поиска
- Синхронизация через триггеры
```

## Ключевые изменения

### `pyproject.toml` - добавить зависимости

- `aiosqlite>=0.19.0`, `alembic>=1.12.0`

### `src/config.py` - обновить конфигурацию

- Добавить: `database_path: str` (по умолчанию `data/bot.db`)
- **Удалить**: `max_storage_size`, `storage_ttl_hours`

### Создать структуру для БД

- `data/.gitkeep` - создать папку для хранения SQLite файла
- `.env.example` - добавить `DATABASE_PATH=data/bot.db`

### `src/database/repository.py` - создать слой БД

**Важно:** Все запросы к БД - **прямой SQL без ORM** (aiosqlite напрямую)

**DatabaseManager** (синглтон):

- `async init()` - открыть соединение aiosqlite, настроить PRAGMA
- `async close()` - закрыть соединение
- `async execute(query, params)` - выполнить SQL
- `async fetchone(query, params)` - вернуть одну строку как dict
- `async fetchall(query, params)` - вернуть все строки как list[dict]

**UserRepository**:

- `async get_or_create()` - INSERT OR IGNORE + SELECT (прямой SQL)
- `async update_last_accessed()` - UPDATE с CURRENT_TIMESTAMP
- `async update_role()` - UPDATE current_role
- `async soft_delete()` - UPDATE deleted_at

**MessageRepository**:

- `async create()` - INSERT с вычислением length = len(content)
- `async get_recent()` - SELECT с ORDER BY created_at DESC LIMIT
- `async soft_delete_all_for_user()` - UPDATE deleted_at для всех сообщений юзера
- `async search_fts()` - SELECT через messages_fts JOIN

### Удалить файлы

- `src/user.py`, `src/conversation.py`

### `src/protocols.py` - удалить устаревшие интерфейсы

- **Удалить**: `IUserStorage`, `IConversationStorage`

### `src/dependencies.py` - заменить storage на repositories

```python
@dataclass
class BotDependencies:
    user_repo: UserRepository
    message_repo: MessageRepository
    llm_client: ILLMClient
    role_manager: IRoleManager
    config: Config
```

### `src/handlers/handlers.py` - рефакторинг

- `deps.user_storage` → `deps.user_repo`
- `conversation.add_message()` → `await deps.message_repo.create(user_id, role, content)`
- `conversation.get_context()` → формирование из БД:
```python
messages = await deps.message_repo.get_recent(user_id, limit=deps.config.max_context_messages)
context = [{"role": "system", "content": system_prompt}]
context.extend([{"role": m["role"], "content": m["content"]} for m in reversed(messages)])
```


### `src/main.py` - интеграция

```python
db_manager = DatabaseManager(config.database_path)
await db_manager.init()
# создать repositories, обновить dependencies
# в finally: await db_manager.close()
```

## Alembic и миграции

- `alembic init alembic`
- Настроить `alembic.ini` для async: `sqlite+aiosqlite:///./data/bot.db`
- Создать `001_initial_schema.py`: users, messages, messages_fts, триггеры FTS5

## Docker

- **Dockerfile** (multi-stage): builder с uv + runtime
- **entrypoint.sh**: `alembic upgrade head` → `python -m src.main`
- **docker-compose.yml**: volume для /app/data и /app/logs, env_file: .env
- **.dockerignore**: исключить .venv, .git, **pycache**, logs, .env
- **Важно:** Создать .env с переменными окружения для docker-compose

## Критерии готовности

- ✅ История сообщений сохраняется между перезапусками
- ✅ Soft delete работает (deleted_at)
- ✅ Поля created_at и length заполняются автоматически
- ✅ Все тесты проходят
- ✅ Миграции применяются и откатываются
- ✅ Docker: `docker-compose up` работает

### To-dos

- [ ] Подготовка инфраструктуры: добавить зависимости (aiosqlite, alembic) в pyproject.toml, обновить config.py (database_path, удалить storage параметры), создать data/.gitkeep и .env.example
- [ ] Настройка Alembic и миграции: инициализировать alembic, настроить alembic.ini/env.py для async, создать первую миграцию 001_initial_schema.py (users с current_role, messages с length/created_at/FOREIGN KEY, messages_fts, триггеры)
- [ ] Реализация слоя данных: создать src/database/repository.py с DatabaseManager, UserRepository, MessageRepository (прямой SQL без ORM через aiosqlite)
- [ ] Рефакторинг существующего кода: обновить protocols.py (удалить IUserStorage/IConversationStorage), удалить src/user.py и src/conversation.py, обновить BotDependencies в dependencies.py
- [ ] Интеграция с приложением: рефакторинг handlers.py для работы с repositories, интеграция DatabaseManager в main.py (init/close)
- [ ] Docker инфраструктура: создать Dockerfile (multi-stage), docker-compose.yml, entrypoint.sh с миграциями, .dockerignore, настроить .env для compose
- [ ] Тестирование: создать tests/test_repository.py, обновить существующие тесты для работы с repositories, добавить тесты миграций
- [ ] Документация README: обновить README.md с документацией по БД (схема, миграции), Docker (запуск, volumes), проверить критерии готовности
- [ ] Актуализация документации проекта: обновить docs/vision.md и docs/idea.md на соответствие реализованным изменениям (переход на персистентное хранение в БД)
- [ ] Обновление roadmap: добавить ссылку на sprint-s1-database-bc5c0f7f.plan.md в таблицу спринтов в docs/roadmap.md, обновить статус SP1 на "В работе"