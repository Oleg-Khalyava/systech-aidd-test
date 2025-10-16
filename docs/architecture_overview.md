# 🏗️ Обзор архитектуры проекта

> **Текущее состояние:** v2.0 Production Ready | 98 тестов | 71% покрытие

## 📐 Общая архитектура

```mermaid
graph TB
    User[👤 Telegram User]
    TG[📱 Telegram API]
    Bot[🤖 Bot aiogram]
    MW1[⏱️ Rate Limit Middleware]
    MW2[💉 DI Middleware]
    Handlers[🎯 Handlers]
    Deps[🔧 BotDependencies]
    UserStore[👥 UserStorage]
    ConvStore[💬 ConversationStorage]
    RoleM[🎭 RoleManager]
    LLM[🧠 LLM Client]
    OpenRouter[🌐 OpenRouter API]
    Prompts[📄 Prompts Files]

    User -->|сообщение| TG
    TG -->|webhook/polling| Bot
    Bot --> MW1
    MW1 --> MW2
    MW2 --> Handlers
    Handlers --> Deps
    Deps --> UserStore
    Deps --> ConvStore
    Deps --> RoleM
    Deps --> LLM
    RoleM -.->|читает| Prompts
    LLM -->|API запрос| OpenRouter
    OpenRouter -->|ответ LLM| LLM
    LLM --> Handlers
    Handlers -->|ответ| Bot
    Bot -->|отправка| TG
    TG -->|доставка| User

    style User fill:#4A90E2,stroke:#2E5C8A,color:#fff
    style Bot fill:#50C878,stroke:#2E8B57,color:#fff
    style MW1 fill:#FFB347,stroke:#CC8B00,color:#000
    style MW2 fill:#FFB347,stroke:#CC8B00,color:#000
    style Handlers fill:#9370DB,stroke:#6A4CA9,color:#fff
    style Deps fill:#E8B4F0,stroke:#B565D8,color:#000
    style LLM fill:#FF6B6B,stroke:#CC5555,color:#fff
    style OpenRouter fill:#4ECDC4,stroke:#3AA39B,color:#fff
    style RoleM fill:#F7DC6F,stroke:#D4AF37,color:#000
```

## 🔄 Поток обработки сообщения

```mermaid
sequenceDiagram
    participant U as 👤 User
    participant B as 🤖 Bot
    participant RL as ⏱️ RateLimit
    participant H as 🎯 Handler
    participant D as 🔧 Deps
    participant C as 💬 Conversation
    participant R as 🎭 RoleManager
    participant L as 🧠 LLMClient
    participant O as 🌐 OpenRouter

    U->>B: Текстовое сообщение
    B->>RL: Проверка rate limit
    alt Слишком частые запросы
        RL-->>B: ❌ Блокировка
        B-->>U: ⏳ Подожди 2 секунды
    else Запрос разрешен
        RL->>H: Передача управления
        H->>D: Получить зависимости
        D->>C: Получить/создать диалог
        C-->>H: Conversation объект
        H->>R: Получить system prompt
        R-->>H: Промпт роли
        H->>C: Добавить сообщение user
        H->>C: Сформировать контекст
        C-->>H: История + system prompt
        H->>L: Отправить в LLM
        L->>O: API запрос
        O-->>L: Ответ от модели
        L-->>H: Текст ответа
        H->>C: Сохранить ответ assistant
        H->>B: Отправить ответ
        B->>U: 💬 Ответ от бота
    end

    style U fill:#4A90E2,stroke:#2E5C8A,color:#fff
    style B fill:#50C878,stroke:#2E8B57,color:#fff
    style RL fill:#FFB347,stroke:#CC8B00,color:#000
    style H fill:#9370DB,stroke:#6A4CA9,color:#fff
    style L fill:#FF6B6B,stroke:#CC5555,color:#fff
    style O fill:#4ECDC4,stroke:#3AA39B,color:#fff
```

## 📦 Компоненты системы

```mermaid
graph LR
    subgraph Core["🎯 Ядро бота"]
        Bot[Bot<br/>aiogram wrapper]
        Config[Config<br/>env vars]
        Main[Main<br/>точка входа]
    end

    subgraph MW["⚙️ Middlewares"]
        RateLimit[RateLimitMiddleware<br/>2 сек между запросами]
        DI[DIMiddleware<br/>инъекция зависимостей]
    end

    subgraph Handlers["🎯 Обработчики"]
        CmdStart[/start]
        CmdClear[/clear]
        CmdRole[/role]
        CmdHelp[/help]
        TextHandler[Текстовые сообщения]
    end

    subgraph Storage["💾 Хранилище In-Memory"]
        UserStorage[UserStorage<br/>LRU + TTL]
        ConvStorage[ConversationStorage<br/>LRU + TTL]
    end

    subgraph Logic["🧠 Бизнес-логика"]
        User[User<br/>dataclass]
        Conversation[Conversation<br/>история диалога]
        RoleManager[RoleManager<br/>управление ролями]
        Validators[Validators<br/>валидация input]
        Metrics[BotMetrics<br/>статистика]
    end

    subgraph External["🌐 Внешние сервисы"]
        LLMClient[LLM Client<br/>retry logic]
        OpenRouter[OpenRouter API<br/>gpt-oss-20b]
    end

    subgraph Files["📁 Файлы"]
        Prompts[prompts/*.txt<br/>системные промпты]
        Logs[logs/bot.log<br/>ротация 10MB]
    end

    Main --> Bot
    Main --> Config
    Bot --> MW
    MW --> Handlers
    Handlers --> Storage
    Handlers --> Logic
    Logic --> External
    RoleManager -.-> Prompts
    Logic -.-> Logs

    style Core fill:#50C878,stroke:#2E8B57,color:#fff
    style MW fill:#FFB347,stroke:#CC8B00,color:#000
    style Handlers fill:#9370DB,stroke:#6A4CA9,color:#fff
    style Storage fill:#4A90E2,stroke:#2E5C8A,color:#fff
    style Logic fill:#E8B4F0,stroke:#B565D8,color:#000
    style External fill:#FF6B6B,stroke:#CC5555,color:#fff
    style Files fill:#F7DC6F,stroke:#D4AF37,color:#000
```

## 🗂️ Структура классов

```mermaid
classDiagram
    class BotDependencies {
        +config: Config
        +user_storage: IUserStorage
        +conversation_storage: IConversationStorage
        +llm_client: ILLMClient
        +role_manager: IRoleManager
        +metrics: BotMetrics
    }

    class User {
        +chat_id: int
        +username: str|None
        +first_name: str
        +created_at: datetime
    }

    class Conversation {
        -chat_id: int
        -messages: list
        -max_messages: int
        +add_message(role, content)
        +get_messages() list
        +clear()
        +get_context_with_prompt(system_prompt) list
    }

    class RoleManager {
        -prompt_file: Path
        -system_prompt: str
        +get_system_prompt() str
        +get_role_description() str
        +reload_prompt()
    }

    class LLMClient {
        -client: OpenAI
        -model: str
        -max_retries: int
        +send_message(messages) str
    }

    class UserStorage {
        -users: OrderedDict
        -max_size: int
        -ttl: timedelta
        +get_or_create(chat_id) User
        +cleanup_expired()
    }

    class ConversationStorage {
        -conversations: OrderedDict
        -max_size: int
        -ttl: timedelta
        +get_or_create(chat_id) Conversation
        +cleanup_expired()
    }

    class BotMetrics {
        +total_requests: int
        +total_errors: int
        +total_tokens: int
        +total_cost: float
        +increment_request()
        +get_summary() dict
    }

    BotDependencies --> UserStorage
    BotDependencies --> ConversationStorage
    BotDependencies --> RoleManager
    BotDependencies --> LLMClient
    BotDependencies --> BotMetrics
    UserStorage --> User
    ConversationStorage --> Conversation

    style BotDependencies fill:#E8B4F0,stroke:#B565D8,color:#000
    style User fill:#4A90E2,stroke:#2E5C8A,color:#fff
    style Conversation fill:#4A90E2,stroke:#2E5C8A,color:#fff
    style RoleManager fill:#F7DC6F,stroke:#D4AF37,color:#000
    style LLMClient fill:#FF6B6B,stroke:#CC5555,color:#fff
    style UserStorage fill:#50C878,stroke:#2E8B57,color:#fff
    style ConversationStorage fill:#50C878,stroke:#2E8B57,color:#fff
    style BotMetrics fill:#FFB347,stroke:#CC8B00,color:#000
```

## 🎭 Управление ролями

```mermaid
graph TB
    subgraph Init["🚀 Инициализация"]
        Start[main.py запуск]
        LoadConfig[Загрузка Config]
        CreateRM[Создание RoleManager]
        ReadFile[Чтение prompts/nutritionist.txt]
    end

    subgraph Usage["💬 Использование"]
        GetPrompt[Handler запрашивает prompt]
        FormContext[Формирование контекста]
        SendLLM[Отправка в LLM]
    end

    subgraph Commands["⌨️ Команды"]
        RoleCmd[/role команда]
        ShowDesc[Показать описание роли]
        HelpCmd[/help команда]
        ShowCmds[Показать команды]
    end

    Start --> LoadConfig
    LoadConfig --> CreateRM
    CreateRM --> ReadFile
    ReadFile -->|Успех| GetPrompt
    ReadFile -->|Ошибка| Exit[❌ Выход с ошибкой]

    GetPrompt --> FormContext
    FormContext --> SendLLM

    RoleCmd --> ShowDesc
    HelpCmd --> ShowCmds

    style Init fill:#50C878,stroke:#2E8B57,color:#fff
    style Usage fill:#9370DB,stroke:#6A4CA9,color:#fff
    style Commands fill:#FFB347,stroke:#CC8B00,color:#000
    style Exit fill:#FF6B6B,stroke:#CC5555,color:#fff
```

## 💾 Управление памятью (LRU + TTL)

```mermaid
graph LR
    subgraph Storage["📦 Storage"]
        OD[OrderedDict<br/>max_size=1000<br/>ttl=24h]
    end

    subgraph Operations["🔄 Операции"]
        Add[Добавить запись]
        Get[Получить запись]
        Cleanup[Очистка expired]
    end

    subgraph Checks["✅ Проверки"]
        CheckSize{Размер >= max_size?}
        CheckTTL{Старше TTL?}
    end

    Add --> CheckSize
    CheckSize -->|Да| RemoveOldest[Удалить старейшую]
    CheckSize -->|Нет| StoreNew[Сохранить новую]
    RemoveOldest --> StoreNew

    Get --> CheckTTL
    CheckTTL -->|Да| Remove[Удалить + вернуть None]
    CheckTTL -->|Нет| Return[Вернуть данные]

    Cleanup --> LoopAll[Перебрать все записи]
    LoopAll --> CheckTTL

    style Storage fill:#4A90E2,stroke:#2E5C8A,color:#fff
    style Operations fill:#50C878,stroke:#2E8B57,color:#fff
    style Checks fill:#FFB347,stroke:#CC8B00,color:#000
```

## 🔒 Безопасность и защита

```mermaid
graph TB
    subgraph Input["📥 Входящие данные"]
        Message[Сообщение от User]
    end

    subgraph Security["🛡️ Защитные слои"]
        RL[Rate Limiting<br/>1 сообщение / 2 сек]
        Val[Валидация<br/>макс 4000 символов]
        Err[Error Handling<br/>скрытие внутренних ошибок]
    end

    subgraph Processing["⚙️ Обработка"]
        Handle[Handler]
        LLM[LLM Client<br/>retry logic x3]
    end

    subgraph Output["📤 Ответ"]
        Safe[Безопасный ответ User]
        Log[Детальный лог в файл]
    end

    Message --> RL
    RL -->|✅ OK| Val
    RL -->|❌ Block| RateLimitMsg[⏳ Подожди]
    Val -->|✅ OK| Handle
    Val -->|❌ Invalid| ValError[❌ Слишком длинное]
    Handle --> LLM
    LLM -->|Успех| Safe
    LLM -->|Ошибка| Err
    Err --> Safe
    Safe --> User[👤 User]
    Handle -.-> Log
    LLM -.-> Log

    style Security fill:#FF6B6B,stroke:#CC5555,color:#fff
    style Processing fill:#9370DB,stroke:#6A4CA9,color:#fff
    style Input fill:#4A90E2,stroke:#2E5C8A,color:#fff
    style Output fill:#50C878,stroke:#2E8B57,color:#fff
```

## 🧪 Тестирование

```mermaid
graph TB
    subgraph Tests["📊 98 тестов, 71% покрытие"]
        Unit[Unit Tests<br/>80 тестов]
        Integration[Integration Tests<br/>18 тестов]
    end

    subgraph Coverage["📈 Coverage по модулям"]
        High[Высокое 95-100%<br/>config, user, conversation,<br/>handlers, metrics, storage]
        Medium[Среднее 90-95%<br/>validators, role_manager]
        Low[Низкое 0%<br/>main, bot, logger, llm<br/>точки входа и обертки]
    end

    subgraph Quality["✅ Качество кода"]
        Black[Black<br/>форматирование]
        Ruff[Ruff<br/>линтер]
        Mypy[Mypy strict<br/>типизация]
    end

    Tests --> Coverage
    Coverage --> Quality

    style Tests fill:#9370DB,stroke:#6A4CA9,color:#fff
    style Coverage fill:#FFB347,stroke:#CC8B00,color:#000
    style Quality fill:#50C878,stroke:#2E8B57,color:#fff
    style High fill:#50C878,stroke:#2E8B57,color:#fff
    style Medium fill:#F7DC6F,stroke:#D4AF37,color:#000
    style Low fill:#FF6B6B,stroke:#CC5555,color:#fff
```

## 📋 Команды бота

```mermaid
stateDiagram-v2
    [*] --> Idle: Запуск бота

    Idle --> Start: /start
    Start --> ActiveDialog: Инициализация

    ActiveDialog --> SendMessage: Текстовое сообщение
    SendMessage --> Processing: Обработка
    Processing --> LLMRequest: Формирование контекста
    LLMRequest --> Response: Ответ от LLM
    Response --> ActiveDialog: Возврат в диалог

    ActiveDialog --> ShowRole: /role
    ShowRole --> ActiveDialog: Описание роли

    ActiveDialog --> ShowHelp: /help
    ShowHelp --> ActiveDialog: Список команд

    ActiveDialog --> Clear: /clear
    Clear --> ActiveDialog: Очистка истории

    style Idle fill:#4A90E2,stroke:#2E5C8A,color:#fff
    style ActiveDialog fill:#50C878,stroke:#2E8B57,color:#fff
    style Processing fill:#9370DB,stroke:#6A4CA9,color:#fff
    style LLMRequest fill:#FF6B6B,stroke:#CC5555,color:#fff
```

## 📊 Метрики и мониторинг

```mermaid
graph LR
    subgraph Events["📥 События"]
        Req[Запрос пользователя]
        Err[Ошибка]
        Token[Токены LLM]
    end

    subgraph Metrics["📈 BotMetrics"]
        Counter[Счетчики<br/>requests, errors]
        Usage[Использование<br/>tokens, cost]
        Timestamp[Временные метки]
    end

    subgraph Logging["📝 Логирование"]
        File[bot.log<br/>ротация 10MB x 5]
        Format[Timestamp + Level + Message]
    end

    subgraph Monitoring["👁️ Мониторинг"]
        Stats[Команда /stats<br/>планируется]
        Summary[get_summary<br/>доступно сейчас]
    end

    Req --> Counter
    Err --> Counter
    Token --> Usage

    Counter --> Summary
    Usage --> Summary
    Timestamp --> Summary

    Req -.-> File
    Err -.-> File
    Token -.-> File

    Summary --> Stats

    style Events fill:#4A90E2,stroke:#2E5C8A,color:#fff
    style Metrics fill:#FFB347,stroke:#CC8B00,color:#000
    style Logging fill:#9370DB,stroke:#6A4CA9,color:#fff
    style Monitoring fill:#50C878,stroke:#2E8B57,color:#fff
```

## 🎯 Dependency Injection

```mermaid
graph TB
    subgraph Creation["🏗️ Создание зависимостей"]
        Main[main.py]
        Config[Config.load]
        UserS[UserStorage]
        ConvS[ConversationStorage]
        Role[RoleManager]
        Client[LLMClient]
        Met[BotMetrics]
        Container[BotDependencies]
    end

    subgraph Injection["💉 Инъекция"]
        MW[DI Middleware]
        Handler[Handler функции]
    end

    subgraph Usage["🎯 Использование"]
        GetUser[deps.user_storage]
        GetConv[deps.conversation_storage]
        GetRole[deps.role_manager]
        SendLLM[deps.llm_client]
    end

    Main --> Config
    Config --> UserS
    Config --> ConvS
    Config --> Role
    Config --> Client
    Config --> Met
    UserS --> Container
    ConvS --> Container
    Role --> Container
    Client --> Container
    Met --> Container

    Container --> MW
    MW --> Handler

    Handler --> GetUser
    Handler --> GetConv
    Handler --> GetRole
    Handler --> SendLLM

    style Creation fill:#50C878,stroke:#2E8B57,color:#fff
    style Injection fill:#FFB347,stroke:#CC8B00,color:#000
    style Usage fill:#9370DB,stroke:#6A4CA9,color:#fff
```

## 🚀 Деплой и запуск

```mermaid
graph LR
    subgraph Setup["⚙️ Настройка"]
        Clone[git clone]
        Install[make install<br/>uv sync]
        Env[.env файл<br/>токены]
    end

    subgraph Run["▶️ Запуск"]
        Start[make run<br/>python -m src.main]
        Init[Инициализация<br/>dependencies]
        Poll[Polling<br/>aiogram]
    end

    subgraph Dev["🛠️ Разработка"]
        Test[make test<br/>pytest]
        Lint[make lint<br/>ruff]
        Type[make type-check<br/>mypy]
        Format[make format<br/>black]
        Check[make check<br/>все проверки]
    end

    Clone --> Install
    Install --> Env
    Env --> Start
    Start --> Init
    Init --> Poll

    Dev --> Check

    style Setup fill:#4A90E2,stroke:#2E5C8A,color:#fff
    style Run fill:#50C878,stroke:#2E8B57,color:#fff
    style Dev fill:#FFB347,stroke:#CC8B00,color:#000
```

---

## 📌 Ключевые особенности

| Аспект | Реализация | Статус |
|--------|-----------|--------|
| **Архитектура** | Dependency Injection + Protocol interfaces | ✅ Production |
| **Безопасность** | Rate limiting + валидация + error hiding | ✅ Production |
| **Память** | LRU cache + TTL (макс 1000, 24ч) | ✅ Production |
| **Тестирование** | 98 тестов, 71% покрытие, TDD подход | ✅ Production |
| **Качество кода** | Black + Ruff + Mypy strict | ✅ Production |
| **Мониторинг** | Логирование + метрики | ✅ Production |
| **Роли** | Файловые промпты + RoleManager | ✅ Production |
| **Retry logic** | 3 попытки для LLM API | ✅ Production |

---

## 🔗 Связанные документы

- [vision.md](vision.md) - Техническое видение и принципы
- [tasklist.md](tasklists/tasklist-sp0.md) - План разработки Sprint 0 (все итерации завершены)
- [code_review_summary.md](code_review_summary.md) - Результаты code review
- [ITERATION_5_REPORT.md](../ITERATION_5_REPORT.md) - Отчет о последней итерации
- [presentation.md](../presentation.md) - Презентация проекта



