"""Тесты для класса Conversation и ConversationStorage"""

from datetime import datetime, timedelta

from src.conversation import Conversation, ConversationStorage


def test_conversation_creation():
    """Тест создания диалога"""
    conversation = Conversation(chat_id=123456)

    assert conversation.chat_id == 123456
    assert conversation.messages == []


def test_conversation_add_message():
    """Тест добавления сообщения в диалог"""
    conversation = Conversation(chat_id=123456)

    conversation.add_message("user", "Hello")

    assert len(conversation.messages) == 1
    assert conversation.messages[0] == {"role": "user", "content": "Hello"}


def test_conversation_add_multiple_messages():
    """Тест добавления нескольких сообщений"""
    conversation = Conversation(chat_id=123456)

    conversation.add_message("user", "Hello")
    conversation.add_message("assistant", "Hi there!")
    conversation.add_message("user", "How are you?")

    assert len(conversation.messages) == 3
    assert conversation.messages[0]["role"] == "user"
    assert conversation.messages[1]["role"] == "assistant"
    assert conversation.messages[2]["role"] == "user"


def test_conversation_get_context_simple():
    """Тест получения контекста диалога"""
    conversation = Conversation(chat_id=123456)

    conversation.add_message("user", "Hello")
    conversation.add_message("assistant", "Hi!")

    context = conversation.get_context(max_messages=10, system_prompt="You are a helpful assistant")

    assert len(context) == 3  # system + 2 messages
    assert context[0] == {"role": "system", "content": "You are a helpful assistant"}
    assert context[1] == {"role": "user", "content": "Hello"}
    assert context[2] == {"role": "assistant", "content": "Hi!"}


def test_conversation_get_context_with_limit():
    """Тест получения контекста с ограничением количества сообщений"""
    conversation = Conversation(chat_id=123456)

    # Добавляем 5 сообщений
    for i in range(5):
        conversation.add_message("user", f"Message {i}")

    # Запрашиваем только последние 2
    context = conversation.get_context(max_messages=2, system_prompt="System")

    # system + 2 последних сообщения
    assert len(context) == 3
    assert context[0]["role"] == "system"
    assert context[1]["content"] == "Message 3"
    assert context[2]["content"] == "Message 4"


def test_conversation_get_context_limit_greater_than_messages():
    """Тест получения контекста когда лимит больше количества сообщений"""
    conversation = Conversation(chat_id=123456)

    conversation.add_message("user", "Hello")

    context = conversation.get_context(max_messages=100, system_prompt="System")

    assert len(context) == 2  # system + 1 message


def test_conversation_clear():
    """Тест очистки истории диалога"""
    conversation = Conversation(chat_id=123456)

    conversation.add_message("user", "Hello")
    conversation.add_message("assistant", "Hi!")
    conversation.add_message("user", "How are you?")

    assert len(conversation.messages) == 3

    conversation.clear()

    assert len(conversation.messages) == 0


def test_conversation_clear_empty():
    """Тест очистки пустого диалога"""
    conversation = Conversation(chat_id=123456)

    conversation.clear()

    assert len(conversation.messages) == 0


def test_conversation_storage_initialization():
    """Тест инициализации хранилища диалогов"""
    storage = ConversationStorage()
    assert storage._conversations == {}


def test_conversation_storage_get_or_create_new():
    """Тест создания нового диалога в хранилище"""
    storage = ConversationStorage()

    conversation = storage.get_or_create(123456)

    assert conversation.chat_id == 123456
    assert len(conversation.messages) == 0
    assert len(storage._conversations) == 1


def test_conversation_storage_get_or_create_existing():
    """Тест получения существующего диалога из хранилища"""
    storage = ConversationStorage()

    # Создаем и модифицируем диалог
    conv1 = storage.get_or_create(123456)
    conv1.add_message("user", "Test message")

    # Получаем тот же диалог
    conv2 = storage.get_or_create(123456)

    assert conv1 is conv2
    assert len(conv2.messages) == 1
    assert conv2.messages[0]["content"] == "Test message"
    assert len(storage._conversations) == 1


def test_conversation_storage_get_existing():
    """Тест получения существующего диалога методом get"""
    storage = ConversationStorage()

    # Создаем диалог
    storage.get_or_create(123456)

    # Получаем через get
    conversation = storage.get(123456)

    assert conversation is not None
    assert conversation.chat_id == 123456


def test_conversation_storage_get_nonexistent():
    """Тест получения несуществующего диалога методом get"""
    storage = ConversationStorage()

    conversation = storage.get(999999)

    assert conversation is None


def test_conversation_storage_multiple_conversations():
    """Тест хранения нескольких диалогов"""
    storage = ConversationStorage()

    conv1 = storage.get_or_create(111)
    conv1.add_message("user", "Message 1")

    conv2 = storage.get_or_create(222)
    conv2.add_message("user", "Message 2")

    conv3 = storage.get_or_create(333)
    conv3.add_message("user", "Message 3")

    assert len(storage._conversations) == 3
    conv1 = storage.get(111)
    conv2 = storage.get(222)
    conv3 = storage.get(333)
    assert conv1 is not None and conv1.messages[0]["content"] == "Message 1"
    assert conv2 is not None and conv2.messages[0]["content"] == "Message 2"
    assert conv3 is not None and conv3.messages[0]["content"] == "Message 3"


def test_conversation_get_context_preserves_order():
    """Тест что get_context сохраняет порядок сообщений"""
    conversation = Conversation(chat_id=123456)

    conversation.add_message("user", "First")
    conversation.add_message("assistant", "Second")
    conversation.add_message("user", "Third")
    conversation.add_message("assistant", "Fourth")

    context = conversation.get_context(max_messages=4, system_prompt="System")

    assert context[1]["content"] == "First"
    assert context[2]["content"] == "Second"
    assert context[3]["content"] == "Third"
    assert context[4]["content"] == "Fourth"


def test_conversation_empty_get_context():
    """Тест получения контекста из пустого диалога"""
    conversation = Conversation(chat_id=123456)

    context = conversation.get_context(max_messages=10, system_prompt="System prompt")

    assert len(context) == 1
    assert context[0] == {"role": "system", "content": "System prompt"}


def test_conversation_storage_lru_eviction():
    """Тест LRU eviction при превышении max_size"""
    storage = ConversationStorage(max_size=3, ttl_hours=24)

    # Создаем 3 диалога (заполняем до лимита)
    storage.get_or_create(1)
    storage.get_or_create(2)
    storage.get_or_create(3)

    assert len(storage._conversations) == 3

    # Добавляем 4-ый диалог - должен вытеснить самый старый (1)
    storage.get_or_create(4)

    assert len(storage._conversations) == 3
    assert storage.get(1) is None  # Самый старый удален
    assert storage.get(2) is not None
    assert storage.get(3) is not None
    assert storage.get(4) is not None


def test_conversation_storage_lru_update_on_access():
    """Тест что доступ обновляет LRU порядок"""
    storage = ConversationStorage(max_size=3, ttl_hours=24)

    # Создаем 3 диалога
    storage.get_or_create(1)
    storage.get_or_create(2)
    storage.get_or_create(3)

    # Обращаемся к диалогу 1 (перемещаем его в конец)
    storage.get(1)

    # Добавляем 4-ый - теперь должен вытеснить диалог 2 (не 1)
    storage.get_or_create(4)

    assert len(storage._conversations) == 3
    assert storage.get(1) is not None  # Остался (был обновлен)
    assert storage.get(2) is None  # Удален (самый старый после обновления 1)
    assert storage.get(3) is not None
    assert storage.get(4) is not None


def test_conversation_storage_ttl_cleanup():
    """Тест TTL cleanup устаревших диалогов"""
    storage = ConversationStorage(max_size=100, ttl_hours=0)  # TTL = 0 для быстрого теста

    # Создаем диалог
    conv = storage.get_or_create(1)

    # Устанавливаем last_accessed в прошлое (> TTL)
    conv.last_accessed = datetime.now() - timedelta(hours=1)

    # Пытаемся получить - должен быть удален при cleanup
    result = storage.get(1)

    assert result is None
    assert len(storage._conversations) == 0


def test_conversation_storage_ttl_with_recent_access():
    """Тест что недавно использованные диалоги не удаляются по TTL"""
    storage = ConversationStorage(max_size=100, ttl_hours=24)

    # Создаем диалог
    conv = storage.get_or_create(1)
    conv.add_message("user", "Hello")

    # last_accessed автоматически обновился при add_message

    # Получаем диалог - он должен быть доступен
    result = storage.get(1)

    assert result is not None
    assert result.chat_id == 1
    assert len(result.messages) == 1
