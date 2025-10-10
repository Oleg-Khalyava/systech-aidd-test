"""Тесты для класса User и UserStorage"""

import pytest
from src.user import User, UserStorage


def test_user_creation():
    """Тест создания пользователя"""
    user = User(
        chat_id=123456,
        username="testuser",
        first_name="Test",
        current_role="Test role"
    )
    
    assert user.chat_id == 123456
    assert user.username == "testuser"
    assert user.first_name == "Test"
    assert user.current_role == "Test role"


def test_user_without_username():
    """Тест создания пользователя без username"""
    user = User(
        chat_id=123456,
        username=None,
        first_name="Test",
        current_role="Test role"
    )
    
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
        chat_id=123456,
        username="testuser",
        first_name="Test",
        default_role="Default role"
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
        chat_id=123456,
        username="testuser",
        first_name="Test",
        default_role="Role1"
    )
    
    # Получаем того же пользователя
    user2 = storage.get_or_create(
        chat_id=123456,
        username="newusername",  # Новые данные не должны изменить существующего
        first_name="NewName",
        default_role="Role2"
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
        chat_id=123456,
        username="testuser",
        first_name="Test",
        default_role="Role"
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
        chat_id=111,
        username="user1",
        first_name="User1",
        default_role="Role1"
    )
    
    user2 = storage.get_or_create(
        chat_id=222,
        username="user2",
        first_name="User2",
        default_role="Role2"
    )
    
    user3 = storage.get_or_create(
        chat_id=333,
        username="user3",
        first_name="User3",
        default_role="Role3"
    )
    
    assert len(storage._users) == 3
    assert storage.get(111) == user1
    assert storage.get(222) == user2
    assert storage.get(333) == user3


def test_user_storage_user_without_username():
    """Тест создания пользователя без username в хранилище"""
    storage = UserStorage()
    
    user = storage.get_or_create(
        chat_id=123456,
        username=None,
        first_name="Test",
        default_role="Role"
    )
    
    assert user.username is None
    assert user.first_name == "Test"

