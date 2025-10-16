"""Тесты для repository слоя"""

import pytest
import pytest_asyncio

from src.database import DatabaseManager, MessageRepository, UserRepository


@pytest_asyncio.fixture
async def db_manager():
    """Фикстура для временной БД в памяти"""
    manager = DatabaseManager(":memory:")
    await manager.init()

    # Применяем миграцию вручную для тестовой БД
    await manager.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            username TEXT NULL,
            first_name TEXT NOT NULL,
            current_role TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            last_accessed TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            deleted_at TIMESTAMP NULL
        )
    """)

    await manager.execute("""
        CREATE TABLE messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            length INTEGER NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            deleted_at TIMESTAMP NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    await manager.execute("""
        CREATE INDEX idx_messages_user_created
        ON messages(user_id, created_at)
    """)

    await manager.execute("""
        CREATE VIRTUAL TABLE messages_fts
        USING fts5(content, content='messages', content_rowid='id')
    """)

    await manager.execute("""
        CREATE TRIGGER messages_fts_insert AFTER INSERT ON messages BEGIN
            INSERT INTO messages_fts(rowid, content)
            VALUES (new.id, new.content);
        END
    """)

    await manager.execute("""
        CREATE TRIGGER messages_fts_update AFTER UPDATE ON messages BEGIN
            UPDATE messages_fts
            SET content = new.content
            WHERE rowid = new.id;
        END
    """)

    await manager.execute("""
        CREATE TRIGGER messages_fts_delete AFTER DELETE ON messages BEGIN
            DELETE FROM messages_fts WHERE rowid = old.id;
        END
    """)

    yield manager

    await manager.close()


@pytest_asyncio.fixture
def user_repo(db_manager):
    """Фикстура для UserRepository"""
    return UserRepository(db_manager)


@pytest_asyncio.fixture
def message_repo(db_manager):
    """Фикстура для MessageRepository"""
    return MessageRepository(db_manager)


class TestDatabaseManager:
    """Тесты для DatabaseManager"""

    @pytest.mark.asyncio
    async def test_init_and_close(self):
        """Тест инициализации и закрытия соединения"""
        manager = DatabaseManager(":memory:")
        await manager.init()
        assert manager._connection is not None

        await manager.close()
        assert manager._connection is None

    @pytest.mark.asyncio
    async def test_execute(self, db_manager):
        """Тест выполнения SQL запроса"""
        cursor = await db_manager.execute(
            "INSERT INTO users (id, username, first_name, current_role) VALUES (?, ?, ?, ?)",
            (1, "test_user", "Test", "default")
        )
        assert cursor.lastrowid == 1

    @pytest.mark.asyncio
    async def test_fetchone(self, db_manager):
        """Тест получения одной строки"""
        await db_manager.execute(
            "INSERT INTO users (id, username, first_name, current_role) VALUES (?, ?, ?, ?)",
            (1, "test_user", "Test", "default")
        )

        user = await db_manager.fetchone("SELECT * FROM users WHERE id = ?", (1,))
        assert user is not None
        assert user["id"] == 1
        assert user["username"] == "test_user"

    @pytest.mark.asyncio
    async def test_fetchall(self, db_manager):
        """Тест получения всех строк"""
        await db_manager.execute(
            "INSERT INTO users (id, username, first_name, current_role) VALUES (?, ?, ?, ?)",
            (1, "user1", "User One", "default")
        )
        await db_manager.execute(
            "INSERT INTO users (id, username, first_name, current_role) VALUES (?, ?, ?, ?)",
            (2, "user2", "User Two", "default")
        )

        users = await db_manager.fetchall("SELECT * FROM users ORDER BY id")
        assert len(users) == 2
        assert users[0]["id"] == 1
        assert users[1]["id"] == 2


class TestUserRepository:
    """Тесты для UserRepository"""

    @pytest.mark.asyncio
    async def test_get_or_create_new_user(self, user_repo):
        """Тест создания нового пользователя"""
        user = await user_repo.get_or_create(
            chat_id=123,
            username="test_user",
            first_name="Test User",
            current_role="nutritionist"
        )

        assert user["id"] == 123
        assert user["username"] == "test_user"
        assert user["first_name"] == "Test User"
        assert user["current_role"] == "nutritionist"
        assert user["deleted_at"] is None

    @pytest.mark.asyncio
    async def test_get_or_create_existing_user(self, user_repo):
        """Тест получения существующего пользователя"""
        # Создаем пользователя
        user1 = await user_repo.get_or_create(
            chat_id=123,
            username="test_user",
            first_name="Test User",
            current_role="nutritionist"
        )

        # Получаем того же пользователя
        user2 = await user_repo.get_or_create(
            chat_id=123,
            username="test_user",
            first_name="Test User",
            current_role="nutritionist"
        )

        assert user1["id"] == user2["id"]
        assert user1["created_at"] == user2["created_at"]

    @pytest.mark.asyncio
    async def test_get_by_id(self, user_repo):
        """Тест получения пользователя по ID"""
        await user_repo.get_or_create(
            chat_id=123,
            username="test_user",
            first_name="Test User",
            current_role="nutritionist"
        )

        user = await user_repo.get_by_id(123)
        assert user is not None
        assert user["id"] == 123

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, user_repo):
        """Тест получения несуществующего пользователя"""
        user = await user_repo.get_by_id(999)
        assert user is None

    @pytest.mark.asyncio
    async def test_update_role(self, user_repo):
        """Тест обновления роли пользователя"""
        await user_repo.get_or_create(
            chat_id=123,
            username="test_user",
            first_name="Test User",
            current_role="default"
        )

        await user_repo.update_role(123, "nutritionist")

        user = await user_repo.get_by_id(123)
        assert user["current_role"] == "nutritionist"

    @pytest.mark.asyncio
    async def test_soft_delete(self, user_repo):
        """Тест soft delete пользователя"""
        await user_repo.get_or_create(
            chat_id=123,
            username="test_user",
            first_name="Test User",
            current_role="default"
        )

        await user_repo.soft_delete(123)

        # После soft delete пользователь не должен находиться
        user = await user_repo.get_by_id(123)
        assert user is None


class TestMessageRepository:
    """Тесты для MessageRepository"""

    @pytest_asyncio.fixture(autouse=True)
    async def setup_user(self, user_repo):
        """Создаем тестового пользователя перед каждым тестом"""
        await user_repo.get_or_create(
            chat_id=123,
            username="test_user",
            first_name="Test User",
            current_role="default"
        )

    @pytest.mark.asyncio
    async def test_create_message(self, message_repo):
        """Тест создания сообщения"""
        message_id = await message_repo.create(
            user_id=123,
            role="user",
            content="Hello, bot!"
        )

        assert message_id > 0

    @pytest.mark.asyncio
    async def test_create_message_calculates_length(self, message_repo, db_manager):
        """Тест автоматического вычисления длины сообщения"""
        content = "Test message content"
        message_id = await message_repo.create(
            user_id=123,
            role="user",
            content=content
        )

        # Проверяем, что length вычислен правильно
        message = await db_manager.fetchone(
            "SELECT * FROM messages WHERE id = ?",
            (message_id,)
        )
        assert message["length"] == len(content)

    @pytest.mark.asyncio
    async def test_get_recent(self, message_repo):
        """Тест получения последних сообщений"""
        # Создаем несколько сообщений
        await message_repo.create(123, "user", "Message 1")
        await message_repo.create(123, "assistant", "Response 1")
        await message_repo.create(123, "user", "Message 2")
        await message_repo.create(123, "assistant", "Response 2")

        # Получаем последние 2 сообщения
        messages = await message_repo.get_recent(123, limit=2)

        assert len(messages) == 2
        # Сообщения должны быть в обратном порядке (последние первыми)
        assert messages[0]["content"] == "Response 2"
        assert messages[1]["content"] == "Message 2"

    @pytest.mark.asyncio
    async def test_soft_delete(self, message_repo, db_manager):
        """Тест soft delete сообщения"""
        message_id = await message_repo.create(123, "user", "Test message")

        await message_repo.soft_delete(message_id)

        # Проверяем, что deleted_at установлен
        message = await db_manager.fetchone(
            "SELECT * FROM messages WHERE id = ?",
            (message_id,)
        )
        assert message["deleted_at"] is not None

        # Сообщение не должно возвращаться в get_recent
        messages = await message_repo.get_recent(123, limit=10)
        assert len(messages) == 0

    @pytest.mark.asyncio
    async def test_soft_delete_all_for_user(self, message_repo):
        """Тест soft delete всех сообщений пользователя"""
        await message_repo.create(123, "user", "Message 1")
        await message_repo.create(123, "assistant", "Response 1")
        await message_repo.create(123, "user", "Message 2")

        await message_repo.soft_delete_all_for_user(123)

        # Все сообщения должны быть удалены
        messages = await message_repo.get_recent(123, limit=10)
        assert len(messages) == 0

    @pytest.mark.asyncio
    async def test_search_fts(self, message_repo):
        """Тест полнотекстового поиска"""
        await message_repo.create(123, "user", "I want to eat pizza")
        await message_repo.create(123, "assistant", "Pizza is a great choice!")
        await message_repo.create(123, "user", "What about pasta?")

        # Поиск по слову "pizza"
        results = await message_repo.search_fts("pizza")

        assert len(results) == 2
        assert any("pizza" in msg["content"].lower() for msg in results)

