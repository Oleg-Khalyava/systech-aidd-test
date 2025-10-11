"""Тесты для класса User и UserStorage"""

from datetime import datetime, timedelta

from src.user import User, UserStorage


def test_user_creation():
    """Тест создания пользователя"""
    user = User(chat_id=123456, username="testuser", first_name="Test", current_role="Test role")

    assert user.chat_id == 123456
    assert user.username == "testuser"
    assert user.first_name == "Test"
    assert user.current_role == "Test role"


def test_user_without_username():
    """Тест создания пользователя без username"""
    user = User(chat_id=123456, username=None, first_name="Test", current_role="Test role")

    assert user.chat_id == 123456
    assert user.username is None
    assert user.first_name == "Test"


def test_user_storage_initialization():
    """Тест инициализации хранилища пользователей"""
    storage = UserStorage()
    assert storage._users == {}


def test_user_storage_get_or_create_new():
    """Тест создания нового пользователя в хранилище"""
    storage = UserStorage()

    user = storage.get_or_create(
        chat_id=123456, username="testuser", first_name="Test", default_role="Default role"
    )

    assert user.chat_id == 123456
    assert user.username == "testuser"
    assert user.first_name == "Test"
    assert user.current_role == "Default role"
    assert len(storage._users) == 1


def test_user_storage_get_or_create_existing():
    """Тест получения существующего пользователя из хранилища"""
    storage = UserStorage()

    # Создаем пользователя
    user1 = storage.get_or_create(
        chat_id=123456, username="testuser", first_name="Test", default_role="Role1"
    )

    # Получаем того же пользователя
    user2 = storage.get_or_create(
        chat_id=123456,
        username="newusername",  # Новые данные не должны изменить существующего
        first_name="NewName",
        default_role="Role2",
    )

    # Должен вернуться тот же объект
    assert user1 is user2
    assert user2.username == "testuser"  # Оригинальные данные сохранились
    assert user2.first_name == "Test"
    assert user2.current_role == "Role1"
    assert len(storage._users) == 1


def test_user_storage_get_existing():
    """Тест получения существующего пользователя методом get"""
    storage = UserStorage()

    # Создаем пользователя
    storage.get_or_create(
        chat_id=123456, username="testuser", first_name="Test", default_role="Role"
    )

    # Получаем через get
    user = storage.get(123456)

    assert user is not None
    assert user.chat_id == 123456
    assert user.username == "testuser"


def test_user_storage_get_nonexistent():
    """Тест получения несуществующего пользователя методом get"""
    storage = UserStorage()

    user = storage.get(999999)

    assert user is None


def test_user_storage_multiple_users():
    """Тест хранения нескольких пользователей"""
    storage = UserStorage()

    user1 = storage.get_or_create(
        chat_id=111, username="user1", first_name="User1", default_role="Role1"
    )

    user2 = storage.get_or_create(
        chat_id=222, username="user2", first_name="User2", default_role="Role2"
    )

    user3 = storage.get_or_create(
        chat_id=333, username="user3", first_name="User3", default_role="Role3"
    )

    assert len(storage._users) == 3
    assert storage.get(111) == user1
    assert storage.get(222) == user2
    assert storage.get(333) == user3


def test_user_storage_user_without_username():
    """Тест создания пользователя без username в хранилище"""
    storage = UserStorage()

    user = storage.get_or_create(
        chat_id=123456, username=None, first_name="Test", default_role="Role"
    )

    assert user.username is None
    assert user.first_name == "Test"


def test_user_storage_lru_eviction():
    """Тест LRU eviction при превышении max_size"""
    storage = UserStorage(max_size=3, ttl_hours=24)

    # Создаем 3 пользователей (заполняем до лимита)
    storage.get_or_create(1, "user1", "User1", "Role")
    storage.get_or_create(2, "user2", "User2", "Role")
    storage.get_or_create(3, "user3", "User3", "Role")

    assert len(storage._users) == 3

    # Добавляем 4-го пользователя - должен вытеснить самого старого (1)
    storage.get_or_create(4, "user4", "User4", "Role")

    assert len(storage._users) == 3
    assert storage.get(1) is None  # Самый старый удален
    assert storage.get(2) is not None
    assert storage.get(3) is not None
    assert storage.get(4) is not None


def test_user_storage_lru_update_on_access():
    """Тест что доступ обновляет LRU порядок"""
    storage = UserStorage(max_size=3, ttl_hours=24)

    # Создаем 3 пользователей
    storage.get_or_create(1, "user1", "User1", "Role")
    storage.get_or_create(2, "user2", "User2", "Role")
    storage.get_or_create(3, "user3", "User3", "Role")

    # Обращаемся к пользователю 1 (перемещаем его в конец)
    storage.get(1)

    # Добавляем 4-го - теперь должен вытеснить пользователя 2 (не 1)
    storage.get_or_create(4, "user4", "User4", "Role")

    assert len(storage._users) == 3
    assert storage.get(1) is not None  # Остался (был обновлен)
    assert storage.get(2) is None  # Удален (самый старый после обновления 1)
    assert storage.get(3) is not None
    assert storage.get(4) is not None


def test_user_storage_ttl_cleanup():
    """Тест TTL cleanup устаревших пользователей"""
    storage = UserStorage(max_size=100, ttl_hours=0)  # TTL = 0 для быстрого теста

    # Создаем пользователя
    user = storage.get_or_create(1, "user1", "User1", "Role")

    # Устанавливаем last_accessed в прошлое (> TTL)
    user.last_accessed = datetime.now() - timedelta(hours=1)

    # Пытаемся получить - должен быть удален при cleanup
    result = storage.get(1)

    assert result is None
    assert len(storage._users) == 0


def test_user_storage_ttl_with_recent_access():
    """Тест что недавно использованные пользователи не удаляются по TTL"""
    storage = UserStorage(max_size=100, ttl_hours=24)

    # Создаем пользователя
    storage.get_or_create(1, "user1", "User1", "Role")

    # last_accessed автоматически обновляется при get_or_create

    # Получаем пользователя - он должен быть доступен
    result = storage.get(1)

    assert result is not None
    assert result.chat_id == 1
    assert result.username == "user1"
