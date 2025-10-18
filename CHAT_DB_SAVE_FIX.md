# Исправление: Сохранение сообщений чата в БД

## Проблема
Сообщения из веб-приложения не сохранялись в базу данных. Веб-чат работал только в памяти браузера, и при перезагрузке страницы вся история терялась.

## Причина
API endpoint `/api/chat/message` только обрабатывал запросы и возвращал ответы от LLM, но **не сохранял** сообщения в базу данных. В отличие от Telegram бота (где сохранение было реализовано), веб-API не имел этого функционала.

## Внесенные изменения

### 1. Backend (API) - Добавлено сохранение в БД

#### `api/models.py`
- Добавлено поле `user_id: int` в `ChatRequest` для идентификации веб-пользователей
- Добавлены новые модели:
  - `ChatHistoryMessage` - единичное сообщение из истории
  - `ChatHistoryResponse` - ответ с историей сообщений

#### `api/chat_manager.py`
- Добавлены `MessageRepository` и `UserRepository` для работы с БД
- Обновлен `handle_normal()`:
  - Принимает `user_id` параметр
  - Создает пользователя в БД (если не существует)
  - Сохраняет сообщение пользователя
  - Сохраняет ответ ассистента
- Обновлен `handle_admin()`:
  - Принимает `user_id` параметр
  - Создает пользователя в БД (если не существует)
  - Сохраняет все сообщения (включая ошибки)

#### `api/api_main.py`
- Обновлен endpoint `POST /api/chat/message`:
  - Передает `user_id` в ChatManager
- Добавлен новый endpoint `GET /api/chat/history/{user_id}`:
  - Возвращает историю сообщений пользователя
  - Параметр `limit` для ограничения количества сообщений

### 2. Frontend - Добавлена работа с user_id и историей

#### `frontend/src/types/chat.ts`
- Добавлено поле `user_id` в `ChatRequest`
- Добавлены типы для истории: `ChatHistoryMessage`, `ChatHistoryResponse`

#### `frontend/src/lib/api.ts`
- Обновлен метод `sendChatMessage()`:
  - Принимает `userId` как первый параметр
  - Отправляет `user_id` в запросе
- Добавлен новый метод `getChatHistory()`:
  - Загружает историю сообщений пользователя

#### `frontend/src/components/chat/ai-chat.tsx`
- Добавлена функция `getUserId()`:
  - Генерирует уникальный ID для веб-пользователя
  - Сохраняет в localStorage для постоянства между сеансами
- Добавлена загрузка истории при монтировании компонента:
  - useEffect загружает историю из API
  - Восстанавливает предыдущие сообщения
- Обновлен `handleSend()`:
  - Передает `userId` в API запросе

## Как это работает

### Поток данных при отправке сообщения:

```
1. Пользователь вводит сообщение в веб-интерфейс
   ↓
2. Frontend генерирует/получает user_id из localStorage
   ↓
3. POST /api/chat/message { user_id, message, mode }
   ↓
4. ChatManager.handle_normal(user_id, message):
   - Создает пользователя в БД (если нужно)
   - Сохраняет сообщение пользователя в БД
   - Получает ответ от LLM
   - Сохраняет ответ ассистента в БД
   - Возвращает ответ
   ↓
5. Frontend отображает ответ и обновляет UI
```

### Восстановление истории:

```
1. Пользователь открывает страницу чата
   ↓
2. Frontend получает user_id из localStorage
   ↓
3. GET /api/chat/history/{user_id}
   ↓
4. API запрашивает MessageRepository.get_recent()
   ↓
5. Возвращает историю сообщений из БД
   ↓
6. Frontend восстанавливает чат
```

## Идентификация веб-пользователей

Для веб-пользователей используется генерация `user_id` на основе:
- Текущего timestamp
- Случайного числа
- Сохранение в `localStorage` для постоянства

Формат имени пользователя в БД: `WebUser_{user_id}`

## Проверка работы

После внесения изменений:

1. ✅ Сообщения из веб-чата сохраняются в таблицу `messages`
2. ✅ Веб-пользователи создаются в таблице `users`
3. ✅ История чата загружается при открытии страницы
4. ✅ История сохраняется между сеансами (через localStorage)
5. ✅ Работают оба режима: normal и admin

## База данных

### Таблица users
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT NULL,
    first_name TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_accessed TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL
)
```

Веб-пользователи имеют:
- `id` - сгенерированный числовой ID
- `username` - NULL (нет username в веб-приложении)
- `first_name` - "WebUser_{id}"

### Таблица messages
```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    role TEXT NOT NULL,  -- 'user' или 'assistant'
    content TEXT NOT NULL,
    length INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
)
```

## Дополнительные возможности

Теперь можно:
- Просматривать историю всех веб-чатов в БД
- Анализировать статистику использования веб-приложения
- Использовать FTS (Full-Text Search) для поиска по сообщениям
- Экспортировать историю чатов

## Примечания

- Веб-пользователи и Telegram пользователи хранятся в одной БД
- ID генерируются так, чтобы не конфликтовать с Telegram chat_id
- Soft delete реализован через поле `deleted_at`
- История загружается ограниченно (по умолчанию 50 сообщений)


