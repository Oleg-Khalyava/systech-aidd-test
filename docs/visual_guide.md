# 🎨 Визуальный гайд по проекту

> **Systech AIDD Test** - ИИ-Нутрициолог Telegram-бот
>
> Визуализация с разных точек зрения

---

## 🏗️ Точка зрения: Архитектура системы

### Слоистая архитектура (Layered Architecture)

```mermaid
graph TB
    subgraph Presentation["🎨 Presentation Layer"]
        TG[Telegram API<br/>aiogram 3.x]
        MW[Middlewares<br/>Rate Limit + DI]
    end

    subgraph Application["⚙️ Application Layer"]
        Handlers[Handlers<br/>команды и сообщения]
        Validators[Validators<br/>валидация input]
    end

    subgraph Domain["💼 Domain Layer"]
        User[User Entity]
        Conversation[Conversation Entity]
        RoleManager[Role Manager]
    end

    subgraph Infrastructure["🔧 Infrastructure Layer"]
        Storage[In-Memory Storage<br/>LRU + TTL]
        LLMClient[LLM Client<br/>OpenRouter API]
        Logger[Logger<br/>файловое логирование]
        Metrics[Metrics<br/>статистика]
    end

    subgraph External["🌐 External Services"]
        OpenRouter[OpenRouter API]
        FileSystem[File System<br/>prompts, logs]
    end

    TG --> MW
    MW --> Handlers
    Handlers --> Validators
    Validators --> Domain
    Domain --> Storage
    Domain --> LLMClient
    LLMClient --> OpenRouter
    Handlers --> Logger
    Handlers --> Metrics
    RoleManager -.-> FileSystem
    Logger -.-> FileSystem

    style Presentation fill:#FF6B6B,stroke:#CC5555,stroke-width:3px,color:#fff
    style Application fill:#4ECDC4,stroke:#3AA39B,stroke-width:3px,color:#000
    style Domain fill:#FFE66D,stroke:#D4B942,stroke-width:3px,color:#000
    style Infrastructure fill:#95E1D3,stroke:#6BB0A3,stroke-width:3px,color:#000
    style External fill:#F38181,stroke:#C25A5A,stroke-width:3px,color:#fff
```

---

## 👤 Точка зрения: User Journey

### Путь пользователя от запуска до получения ответа

```mermaid
journey
    title Путешествие пользователя в боте
    section Начало работы
      Найти бота в Telegram: 5: User
      Нажать /start: 5: User
      Прочитать приветствие: 4: User
      Узнать о возможностях: 4: User
    section Взаимодействие
      Задать вопрос о питании: 5: User
      Получить ответ: 5: User, Bot
      Продолжить диалог: 5: User
      Получить контекстный ответ: 5: User, Bot
    section Управление
      Посмотреть /role: 3: User
      Узнать специализацию: 4: User
      Очистить /clear: 4: User
      Начать новый диалог: 5: User
    section Проблемы
      Слишком быстрое сообщение: 1: User
      Получить rate limit: 2: User, Bot
      Подождать 2 секунды: 2: User
      Повторить успешно: 5: User
```

---

## 💻 Точка зрения: Разработчик - Структура кода

### Дерево модулей и их зависимости

```mermaid
graph LR
    subgraph Entry["🚀 Точка входа"]
        Main[main.py]
    end

    subgraph Core["⚡ Ядро"]
        Bot[bot.py]
        Config[config.py]
        Deps[dependencies.py]
        Protocols[protocols.py]
    end

    subgraph Business["💼 Бизнес-логика"]
        User[user.py]
        Conv[conversation.py]
        Role[role_manager.py]
        Valid[validators.py]
        Metr[metrics.py]
    end

    subgraph Handlers["🎯 Обработчики"]
        HandlersMod[handlers/handlers.py]
    end

    subgraph MW["🔀 Middleware"]
        RateLimit[middlewares/rate_limit.py]
        DI[middlewares/dependency_injection.py]
    end

    subgraph LLM["🧠 LLM"]
        Client[llm/client.py]
    end

    subgraph Utils["🛠️ Утилиты"]
        Log[logger.py]
    end

    Main --> Bot
    Main --> Config
    Main --> Deps
    Bot --> MW
    MW --> Handlers
    Handlers --> Business
    Handlers --> Valid
    Business --> LLM
    Deps -.->|использует| Protocols
    Config --> Log

    style Entry fill:#FF5252,stroke:#D32F2F,stroke-width:4px,color:#fff
    style Core fill:#448AFF,stroke:#2962FF,stroke-width:3px,color:#fff
    style Business fill:#69F0AE,stroke:#00C853,stroke-width:3px,color:#000
    style Handlers fill:#FFD740,stroke:#FFC400,stroke-width:3px,color:#000
    style MW fill:#FF6E40,stroke:#FF3D00,stroke-width:3px,color:#fff
    style LLM fill:#E040FB,stroke:#D500F9,stroke-width:3px,color:#fff
    style Utils fill:#64FFDA,stroke:#1DE9B6,stroke-width:3px,color:#000
```

---

## 🔄 Точка зрения: Data Flow

### Как данные проходят через систему

```mermaid
graph TB
    Start([👤 User отправляет сообщение])

    subgraph Input["📥 Входные данные"]
        RawMsg[Raw Message<br/>text + chat_id + metadata]
        Parse[Парсинг Message объекта]
    end

    subgraph Validation["✅ Валидация"]
        CheckRL{Rate Limit<br/>OK?}
        CheckLen{Длина<br/>≤4000?}
        CheckEmpty{Не пустое?}
    end

    subgraph Processing["⚙️ Обработка"]
        GetUser[Получить User<br/>из UserStorage]
        GetConv[Получить Conversation<br/>из ConversationStorage]
        AddMsg[Добавить сообщение<br/>в историю]
    end

    subgraph Context["📝 Формирование контекста"]
        GetPrompt[Получить system prompt<br/>из RoleManager]
        BuildCtx[Собрать контекст:<br/>system + последние 10 сообщений]
    end

    subgraph LLM["🧠 LLM"]
        SendAPI[Отправить в OpenRouter]
        Retry{Ошибка?}
        Response[Получить ответ]
    end

    subgraph Output["📤 Ответ"]
        SaveResp[Сохранить ответ<br/>в историю]
        SendUser[Отправить<br/>пользователю]
        LogMetrics[Логирование<br/>+ Метрики]
    end

    End([👤 User получает ответ])

    Start --> RawMsg --> Parse
    Parse --> CheckRL
    CheckRL -->|❌ Блок| ErrorRL[⏳ Rate limit error]
    CheckRL -->|✅| CheckLen
    CheckLen -->|❌| ErrorLen[❌ Слишком длинное]
    CheckLen -->|✅| CheckEmpty
    CheckEmpty -->|❌| ErrorEmpty[❌ Пустое сообщение]
    CheckEmpty -->|✅| GetUser
    GetUser --> GetConv
    GetConv --> AddMsg
    AddMsg --> GetPrompt
    GetPrompt --> BuildCtx
    BuildCtx --> SendAPI
    SendAPI --> Retry
    Retry -->|Да, retry < 3| SendAPI
    Retry -->|Нет| Response
    Response --> SaveResp
    SaveResp --> SendUser
    SendUser --> LogMetrics
    LogMetrics --> End

    ErrorRL --> End
    ErrorLen --> End
    ErrorEmpty --> End

    style Start fill:#00C853,stroke:#00E676,stroke-width:3px,color:#fff
    style End fill:#00C853,stroke:#00E676,stroke-width:3px,color:#fff
    style Input fill:#2196F3,stroke:#1976D2,stroke-width:2px,color:#fff
    style Validation fill:#FF9800,stroke:#F57C00,stroke-width:2px,color:#fff
    style Processing fill:#9C27B0,stroke:#7B1FA2,stroke-width:2px,color:#fff
    style Context fill:#00BCD4,stroke:#0097A7,stroke-width:2px,color:#fff
    style LLM fill:#E91E63,stroke:#C2185B,stroke-width:2px,color:#fff
    style Output fill:#4CAF50,stroke:#388E3C,stroke-width:2px,color:#fff
```

---

## 🛡️ Точка зрения: Безопасность

### Security Flow - Защитные механизмы

```mermaid
graph TB
    Threat1[🔴 Угроза: Спам]
    Threat2[🔴 Угроза: Большие сообщения]
    Threat3[🔴 Угроза: Утечка данных]
    Threat4[🔴 Угроза: DDoS]

    subgraph Defense1["🛡️ Rate Limiting"]
        RL1[Проверка последнего запроса]
        RL2[Блокировка < 2 сек]
        RL3[Разрешение ≥ 2 сек]
    end

    subgraph Defense2["🛡️ Input Validation"]
        Val1[Проверка длины ≤ 4000]
        Val2[Проверка на пустоту]
        Val3[Санитизация текста]
    end

    subgraph Defense3["🛡️ Error Handling"]
        Err1[Catch всех exceptions]
        Err2[Скрытие внутренних деталей]
        Err3[Безопасное сообщение user]
        Err4[Полный лог в файл]
    end

    subgraph Defense4["🛡️ Memory Management"]
        Mem1[LRU ограничение 1000]
        Mem2[TTL очистка 24ч]
        Mem3[Предотвращение утечек]
    end

    subgraph Safe["✅ Безопасная система"]
        Safe1[Защищенный бот]
        Safe2[Контролируемые ресурсы]
        Safe3[Логирование всех событий]
    end

    Threat1 --> RL1
    Threat4 --> RL1
    RL1 --> RL2
    RL1 --> RL3
    RL2 -.->|Блокировка| Safe1
    RL3 -.->|Пропуск| Val1

    Threat2 --> Val1
    Val1 --> Val2
    Val2 --> Val3
    Val3 -.-> Safe1

    Threat3 --> Err1
    Err1 --> Err2
    Err2 --> Err3
    Err3 --> Err4
    Err4 -.-> Safe3

    RL1 -.-> Mem1
    Mem1 --> Mem2
    Mem2 --> Mem3
    Mem3 -.-> Safe2

    Safe1 --> SafeSystem[🎉 Production Ready]
    Safe2 --> SafeSystem
    Safe3 --> SafeSystem

    style Threat1 fill:#D32F2F,stroke:#B71C1C,stroke-width:3px,color:#fff
    style Threat2 fill:#D32F2F,stroke:#B71C1C,stroke-width:3px,color:#fff
    style Threat3 fill:#D32F2F,stroke:#B71C1C,stroke-width:3px,color:#fff
    style Threat4 fill:#D32F2F,stroke:#B71C1C,stroke-width:3px,color:#fff
    style Defense1 fill:#FFA726,stroke:#F57C00,stroke-width:2px,color:#000
    style Defense2 fill:#FFA726,stroke:#F57C00,stroke-width:2px,color:#000
    style Defense3 fill:#FFA726,stroke:#F57C00,stroke-width:2px,color:#000
    style Defense4 fill:#FFA726,stroke:#F57C00,stroke-width:2px,color:#000
    style Safe fill:#66BB6A,stroke:#43A047,stroke-width:2px,color:#fff
    style SafeSystem fill:#00C853,stroke:#00E676,stroke-width:4px,color:#fff
```

---

## ⚡ Точка зрения: Performance & Memory

### Управление памятью и производительностью

```mermaid
graph LR
    subgraph Problem["⚠️ Проблема"]
        P1[Бесконечный рост памяти]
        P2[Старые данные]
        P3[Медленный доступ]
    end

    subgraph Solution1["💡 LRU Cache"]
        L1[OrderedDict]
        L2[Ограничение max_size=1000]
        L3[Удаление старейших при overflow]
        L4[Move to end при доступе]
    end

    subgraph Solution2["💡 TTL Механизм"]
        T1[Timestamp при создании]
        T2[Проверка возраста]
        T3[Автоудаление > 24ч]
        T4[Фоновая очистка]
    end

    subgraph Result["✅ Результат"]
        R1[Контролируемая память]
        R2[Быстрый доступ O 1]
        R3[Автоматическая очистка]
        R4[Production Ready]
    end

    P1 --> L1
    P1 --> L2
    L1 --> L2
    L2 --> L3
    L3 --> L4

    P2 --> T1
    T1 --> T2
    T2 --> T3
    T3 --> T4

    P3 --> L4

    L4 --> R1
    L4 --> R2
    T4 --> R1
    T4 --> R3

    R1 --> R4
    R2 --> R4
    R3 --> R4

    style Problem fill:#EF5350,stroke:#C62828,stroke-width:3px,color:#fff
    style Solution1 fill:#42A5F5,stroke:#1565C0,stroke-width:2px,color:#fff
    style Solution2 fill:#AB47BC,stroke:#6A1B9A,stroke-width:2px,color:#fff
    style Result fill:#66BB6A,stroke:#2E7D32,stroke-width:3px,color:#fff
    style R4 fill:#00E676,stroke:#00C853,stroke-width:4px,color:#000
```

---

## 🎯 Точка зрения: State Management

### Состояния диалога и переходы

```mermaid
stateDiagram-v2
    [*] --> BotStarted: Запуск бота

    BotStarted --> Idle: Инициализация

    state Idle {
        [*] --> WaitingForUser
        WaitingForUser --> CheckingMessage: Получено сообщение
    }

    state CheckingMessage {
        [*] --> RateLimitCheck
        RateLimitCheck --> ValidationCheck: ✅ Passed
        RateLimitCheck --> RateLimited: ❌ Too Fast
        ValidationCheck --> ProcessingMessage: ✅ Valid
        ValidationCheck --> ValidationError: ❌ Invalid
    }

    state ProcessingMessage {
        [*] --> LoadingContext
        LoadingContext --> BuildingPrompt
        BuildingPrompt --> CallingLLM
        CallingLLM --> ReceivingResponse: Success
        CallingLLM --> RetryingLLM: Error (retry < 3)
        RetryingLLM --> CallingLLM
        RetryingLLM --> LLMError: Max retries
    }

    ProcessingMessage --> SendingResponse: Response ready

    state SendingResponse {
        [*] --> SavingToHistory
        SavingToHistory --> UpdateMetrics
        UpdateMetrics --> SendToUser
    }

    SendingResponse --> Idle: Ответ отправлен
    RateLimited --> Idle: Пауза 2 сек
    ValidationError --> Idle: Уведомление
    LLMError --> Idle: Error handled

    state CommandProcessing {
        [*] --> ParseCommand
        ParseCommand --> StartCommand: /start
        ParseCommand --> ClearCommand: /clear
        ParseCommand --> RoleCommand: /role
        ParseCommand --> HelpCommand: /help
    }

    CheckingMessage --> CommandProcessing: Команда обнаружена
    CommandProcessing --> Idle: Команда выполнена

    Idle --> [*]: Shutdown signal

    note right of BotStarted
        Загрузка конфигурации
        Инициализация dependencies
        Подключение к Telegram
    end note

    note right of ProcessingMessage
        Retry logic: 3 попытки
        Exponential backoff
        Логирование всех попыток
    end note

    note right of SendingResponse
        Сохранение в историю
        Обновление метрик
        Безопасная отправка
    end note
```

---

## 🔌 Точка зрения: Integration & API

### Взаимодействие с внешними сервисами

```mermaid
sequenceDiagram
    participant U as 👤 User
    participant T as 📱 Telegram
    participant B as 🤖 Bot
    participant V as ✅ Validator
    participant S as 💾 Storage
    participant R as 🎭 RoleManager
    participant L as 🧠 LLMClient
    participant O as 🌐 OpenRouter
    participant F as 📁 FileSystem
    participant Log as 📝 Logger

    rect rgb(135, 206, 250)
        note right of U: Пользователь отправляет сообщение
        U->>T: "Как похудеть?"
        T->>B: Message event
    end

    rect rgb(255, 182, 193)
        note right of B: Rate Limiting
        B->>B: Проверка rate limit
        alt Too fast
            B->>T: ⏳ Подожди 2 сек
            T->>U: Rate limit message
        end
    end

    rect rgb(255, 218, 185)
        note right of V: Валидация
        B->>V: Validate message
        V->>V: Check length ≤ 4000
        V->>V: Check not empty
        V-->>B: ✅ Valid
    end

    rect rgb(221, 160, 221)
        note right of S: Работа с хранилищем
        B->>S: Get/Create User
        S-->>B: User object
        B->>S: Get/Create Conversation
        S-->>B: Conversation object
        B->>S: Add user message
    end

    rect rgb(152, 251, 152)
        note right of R: Формирование контекста
        B->>R: Get system prompt
        R->>F: Read prompts/nutritionist.txt
        F-->>R: Prompt content
        R-->>B: System prompt
        B->>S: Get context (last 10 messages)
        S-->>B: Message history
    end

    rect rgb(255, 160, 122)
        note right of L: Запрос к LLM
        B->>L: Send messages
        L->>Log: Log request
        loop Retry до 3 раз
            L->>O: POST /chat/completions
            alt Success
                O-->>L: Response (200 OK)
            else Error
                O-->>L: Error (5xx/timeout)
                L->>L: Wait + Retry
            end
        end
        L->>Log: Log response
        L-->>B: LLM answer
    end

    rect rgb(255, 228, 181)
        note right of B: Сохранение и отправка
        B->>S: Save assistant message
        B->>B: Update metrics
        B->>Log: Log success
        B->>T: Send response
        T->>U: Ответ от нутрициолога
    end

    rect rgb(176, 224, 230)
        note right of U: Продолжение диалога
        U->>T: "А сколько калорий?"
        note over U,O: Контекст сохранён,<br/>следующий ответ учитывает историю
    end
```

---

## 🏛️ Точка зрения: SOLID Principles

### Применение SOLID принципов в архитектуре

```mermaid
graph TB
    subgraph SRP["S - Single Responsibility"]
        SRP1[User.py<br/>только управление пользователем]
        SRP2[Conversation.py<br/>только история диалога]
        SRP3[RoleManager.py<br/>только управление ролями]
        SRP4[Validators.py<br/>только валидация]
    end

    subgraph OCP["O - Open/Closed Principle"]
        OCP1[Protocol интерфейсы<br/>расширяемость без изменений]
        OCP2[Middleware архитектура<br/>новые middleware без изменения ядра]
    end

    subgraph LSP["L - Liskov Substitution"]
        LSP1[Любая реализация IUserStorage<br/>заменяема]
        LSP2[Любая реализация ILLMClient<br/>заменяема]
        LSP3[Любая реализация IRoleManager<br/>заменяема]
    end

    subgraph ISP["I - Interface Segregation"]
        ISP1[IUserStorage<br/>минимальный интерфейс<br/>get_or_create]
        ISP2[ILLMClient<br/>минимальный интерфейс<br/>send_message]
        ISP3[IRoleManager<br/>минимальный интерфейс<br/>3 метода]
    end

    subgraph DIP["D - Dependency Inversion"]
        DIP1[Handler зависит от Protocol]
        DIP2[Не зависит от конкретных классов]
        DIP3[Инъекция через middleware]
        DIP4[BotDependencies контейнер]
    end

    SOLID[🎯 SOLID Architecture]

    SRP --> SOLID
    OCP --> SOLID
    LSP --> SOLID
    ISP --> SOLID
    DIP --> SOLID

    style SRP fill:#FF6B6B,stroke:#CC5555,stroke-width:2px,color:#fff
    style OCP fill:#4ECDC4,stroke:#3AA39B,stroke-width:2px,color:#000
    style LSP fill:#FFE66D,stroke:#D4B942,stroke-width:2px,color:#000
    style ISP fill:#95E1D3,stroke:#6BB0A3,stroke-width:2px,color:#000
    style DIP fill:#F38181,stroke:#C25A5A,stroke-width:2px,color:#fff
    style SOLID fill:#00E676,stroke:#00C853,stroke-width:4px,color:#000
```

---

## 🧪 Точка зрения: Testing Strategy

### Пирамида тестирования

```mermaid
graph TB
    subgraph Pyramid["🔺 Пирамида тестирования"]
        E2E[E2E Tests<br/>0 тестов<br/>опциональны]
        Integration[Integration Tests<br/>18 тестов<br/>критичные flow]
        Unit[Unit Tests<br/>80 тестов<br/>бизнес-логика]
    end

    subgraph Coverage["📊 Покрытие 71%"]
        High[100% Coverage<br/>config, user, conversation<br/>storage, metrics, deps]
        Medium[90-95% Coverage<br/>handlers, validators<br/>role_manager]
        Low[0% Coverage<br/>main, bot, logger<br/>точки входа]
        Ignored[Игнорируется<br/>llm/client.py<br/>внешний API]
    end

    subgraph Quality["✅ Качество"]
        TDD[TDD подход<br/>RED-GREEN-REFACTOR]
        Fast[Быстрые тесты<br/>98 за 4 сек]
        Parallel[Параллельный запуск<br/>pytest-xdist]
    end

    subgraph Tools["🛠️ Инструменты"]
        Pytest[pytest + asyncio]
        Mock[pytest-mock]
        Cov[pytest-cov]
    end

    Unit --> Integration
    Integration --> E2E

    Unit -.-> High
    Unit -.-> Medium
    Integration -.-> Medium
    E2E -.-> Low

    High --> Quality
    Medium --> Quality

    TDD --> Tools
    Fast --> Tools
    Parallel --> Tools

    style E2E fill:#FFE66D,stroke:#D4B942,stroke-width:2px,color:#000
    style Integration fill:#4ECDC4,stroke:#3AA39B,stroke-width:3px,color:#000
    style Unit fill:#66BB6A,stroke:#43A047,stroke-width:4px,color:#fff
    style High fill:#00E676,stroke:#00C853,stroke-width:2px,color:#000
    style Medium fill:#FFD740,stroke:#FFC400,stroke-width:2px,color:#000
    style Low fill:#FF5252,stroke:#D32F2F,stroke-width:2px,color:#fff
    style Quality fill:#448AFF,stroke:#2962FF,stroke-width:2px,color:#fff
```

---

## 📦 Точка зрения: Deployment

### От разработки до production

```mermaid
graph LR
    subgraph Dev["💻 Development"]
        Code[Написание кода]
        Format[make format<br/>black]
        Lint[make lint<br/>ruff]
        Type[make type-check<br/>mypy]
        Test[make test<br/>pytest]
    end

    subgraph CI["🔄 CI/CD готовность"]
        Check[make check<br/>все проверки]
        Coverage[coverage ≥ 70%]
        Quality[quality score 8.7/10]
    end

    subgraph Build["🏗️ Build"]
        UV[uv sync]
        Deps[Установка зависимостей]
        Env[Настройка .env]
    end

    subgraph Deploy["🚀 Production"]
        Server[VPS/Cloud сервер]
        Process[Systemd service]
        Monitor[Логирование + метрики]
    end

    Code --> Format
    Format --> Lint
    Lint --> Type
    Type --> Test
    Test --> Check
    Check --> Coverage
    Coverage --> Quality
    Quality --> UV
    UV --> Deps
    Deps --> Env
    Env --> Server
    Server --> Process
    Process --> Monitor

    style Dev fill:#42A5F5,stroke:#1565C0,stroke-width:2px,color:#fff
    style CI fill:#66BB6A,stroke:#2E7D32,stroke-width:2px,color:#fff
    style Build fill:#FFA726,stroke:#F57C00,stroke-width:2px,color:#000
    style Deploy fill:#AB47BC,stroke:#6A1B9A,stroke-width:2px,color:#fff
```

---

## 🌐 Точка зрения: Technology Stack

### Технологический стек с версиями

```mermaid
graph TB
    subgraph Lang["🐍 Язык"]
        Python[Python 3.11+<br/>современный синтаксис]
    end

    subgraph Framework["🤖 Bot Framework"]
        Aiogram[aiogram 3.x<br/>async Telegram bot]
    end

    subgraph LLM["🧠 AI/LLM"]
        OpenAI[openai SDK<br/>OpenRouter API]
        Model[gpt-oss-20b<br/>через OpenRouter]
    end

    subgraph Tools["🛠️ Dev Tools"]
        UV[uv<br/>package manager]
        Black[black<br/>code formatter]
        Ruff[ruff<br/>fast linter]
        Mypy[mypy<br/>type checker]
    end

    subgraph Testing["🧪 Testing"]
        Pytest[pytest<br/>test framework]
        AsyncIO[pytest-asyncio<br/>async tests]
        Cov[pytest-cov<br/>coverage]
        Mock[pytest-mock<br/>mocking]
    end

    subgraph Storage["💾 Storage"]
        Memory[In-Memory<br/>OrderedDict<br/>LRU + TTL]
    end

    subgraph Config["⚙️ Config"]
        Dotenv[python-dotenv<br/>.env loader]
    end

    subgraph Logging["📝 Logging"]
        StdLogging[Python logging<br/>file rotation]
    end

    Python --> Aiogram
    Python --> OpenAI
    OpenAI --> Model
    Aiogram --> Storage
    Python --> Tools
    Python --> Testing
    Python --> Config
    Python --> Logging

    style Lang fill:#FFD740,stroke:#FFC400,stroke-width:3px,color:#000
    style Framework fill:#00E676,stroke:#00C853,stroke-width:2px,color:#000
    style LLM fill:#E040FB,stroke:#D500F9,stroke-width:2px,color:#fff
    style Tools fill:#448AFF,stroke:#2962FF,stroke-width:2px,color:#fff
    style Testing fill:#FF6E40,stroke:#FF3D00,stroke-width:2px,color:#fff
    style Storage fill:#64FFDA,stroke:#1DE9B6,stroke-width:2px,color:#000
    style Config fill:#FFB74D,stroke:#F57C00,stroke-width:2px,color:#000
    style Logging fill:#4DB6AC,stroke:#00897B,stroke-width:2px,color:#fff
```

---

## 🎭 Точка зрения: Role System

### Система управления ролями

```mermaid
graph TB
    subgraph FileSystem["📁 Файловая система"]
        PromptsDir[prompts/]
        NutFile[nutritionist.txt]
        FutureRole1[doctor.txt<br/>будущее]
        FutureRole2[trainer.txt<br/>будущее]
    end

    subgraph RoleManager["🎭 RoleManager"]
        Init[__init__<br/>загрузка файла]
        Load[load_system_prompt<br/>чтение из файла]
        Get[get_system_prompt<br/>полный промпт]
        Desc[get_role_description<br/>первые 3 строки]
        Reload[reload_prompt<br/>горячая перезагрузка]
    end

    subgraph Usage["💬 Использование"]
        StartCmd[/start команда<br/>показать роль]
        RoleCmd[/role команда<br/>описание]
        MsgHandler[Message handler<br/>формирование контекста]
    end

    subgraph Context["📝 Контекст LLM"]
        SystemMsg[system: промпт роли]
        UserMsgs[user: сообщения]
        AssistMsgs[assistant: ответы]
        APICall[Отправка в OpenRouter]
    end

    PromptsDir --> NutFile
    NutFile --> Init
    Init --> Load
    Load --> Get
    Load --> Desc
    Get --> Reload

    Get --> MsgHandler
    Desc --> StartCmd
    Desc --> RoleCmd

    MsgHandler --> SystemMsg
    SystemMsg --> UserMsgs
    UserMsgs --> AssistMsgs
    AssistMsgs --> APICall

    style FileSystem fill:#FFE082,stroke:#FFB300,stroke-width:2px,color:#000
    style RoleManager fill:#64B5F6,stroke:#1976D2,stroke-width:2px,color:#fff
    style Usage fill:#81C784,stroke:#388E3C,stroke-width:2px,color:#fff
    style Context fill:#BA68C8,stroke:#7B1FA2,stroke-width:2px,color:#fff
```

---

## 📊 Точка зрения: Metrics & Monitoring

### Система метрик и мониторинга

```mermaid
graph LR
    subgraph Events["📥 События"]
        E1[User запрос]
        E2[LLM вызов]
        E3[Ошибка]
        E4[Токены использованы]
    end

    subgraph Collection["📊 Сбор метрик"]
        M1[total_requests++]
        M2[total_errors++]
        M3[total_tokens += N]
        M4[total_cost += $]
        M5[active_users.add]
        M6[start_time]
    end

    subgraph Calculated["🧮 Вычисляемые"]
        C1[uptime<br/>now - start_time]
        C2[error_rate<br/>errors/requests %]
        C3[avg_tokens<br/>tokens/requests]
        C4[cost_per_request<br/>cost/requests]
    end

    subgraph Storage["💾 Хранение"]
        S1[BotMetrics объект<br/>in-memory]
        S2[Логи в файл<br/>logs/bot.log]
    end

    subgraph Output["📤 Вывод"]
        O1[get_summary<br/>dict]
        O2[get_stats_formatted<br/>строка]
        O3[/stats команда<br/>планируется]
    end

    E1 --> M1
    E2 --> M1
    E2 --> M3
    E2 --> M4
    E3 --> M2
    E1 --> M5

    M1 --> C1
    M1 --> C2
    M2 --> C2
    M3 --> C3
    M4 --> C4
    M6 --> C1

    M1 --> S1
    M2 --> S1
    M3 --> S1
    M4 --> S1
    M5 --> S1

    S1 --> O1
    S1 --> O2
    O1 --> O3
    O2 --> O3

    S1 -.-> S2

    style Events fill:#42A5F5,stroke:#1565C0,stroke-width:2px,color:#fff
    style Collection fill:#66BB6A,stroke:#2E7D32,stroke-width:2px,color:#fff
    style Calculated fill:#FFA726,stroke:#F57C00,stroke-width:2px,color:#000
    style Storage fill:#AB47BC,stroke:#6A1B9A,stroke-width:2px,color:#fff
    style Output fill:#26C6DA,stroke:#00838F,stroke-width:2px,color:#fff
```

---

## 🔄 Точка зрения: Lifecycle

### Жизненный цикл приложения

```mermaid
stateDiagram-v2
    [*] --> Starting: python -m src.main

    state Starting {
        [*] --> LoadEnv
        LoadEnv --> ValidateConfig
        ValidateConfig --> InitLogger
        InitLogger --> CreateDependencies
        CreateDependencies --> LoadRolePrompt
        LoadRolePrompt --> InitBot
        InitBot --> RegisterHandlers
        RegisterHandlers --> RegisterMiddlewares
    }

    Starting --> Running: Запуск polling

    state Running {
        [*] --> Polling

        state Polling {
            [*] --> WaitingUpdates
            WaitingUpdates --> ReceiveUpdate: Update
            ReceiveUpdate --> ProcessUpdate
            ProcessUpdate --> WaitingUpdates: Done
        }

        state ProcessUpdate {
            [*] --> Middlewares
            Middlewares --> Handlers
            Handlers --> Response
        }

        state MemoryManagement {
            [*] --> CheckMemory
            CheckMemory --> CleanupLRU: size > max
            CheckMemory --> CleanupTTL: age > 24h
            CleanupLRU --> [*]
            CleanupTTL --> [*]
        }

        Polling --> MemoryManagement: Периодически
        MemoryManagement --> Polling
    }

    Running --> Stopping: SIGINT/SIGTERM

    state Stopping {
        [*] --> StopPolling
        StopPolling --> SaveMetrics
        SaveMetrics --> FlushLogs
        FlushLogs --> CloseConnections
    }

    Stopping --> [*]: Graceful shutdown

    note right of Starting
        Полная инициализация
        Проверка всех зависимостей
        Fail-fast при ошибках
    end note

    note right of Running
        Основной цикл работы
        Обработка сообщений
        Автоматическая очистка памяти
    end note

    note right of Stopping
        Корректное завершение
        Сохранение состояния
        Закрытие соединений
    end note
```

---

## 🎨 Точка зрения: Design Patterns

### Используемые паттерны проектирования

```mermaid
graph TB
    subgraph Creational["🏗️ Порождающие"]
        Factory[Storage Factories<br/>get_or_create pattern]
        DI[Dependency Injection<br/>BotDependencies контейнер]
    end

    subgraph Structural["🔧 Структурные"]
        Facade[Config Facade<br/>упрощение доступа к env]
        Protocol[Protocol Pattern<br/>структурная типизация]
    end

    subgraph Behavioral["⚡ Поведенческие"]
        Strategy[Strategy<br/>разные LLM клиенты]
        Middleware[Chain of Responsibility<br/>middleware pipeline]
        Observer[Observer<br/>metrics + logging]
    end

    subgraph Domain["💼 Доменные"]
        Repository[Repository<br/>UserStorage, ConvStorage]
        Entity[Entity<br/>User, Conversation]
    end

    subgraph Resilience["🛡️ Устойчивость"]
        Retry[Retry Pattern<br/>3 попытки LLM]
        CircuitBreaker[Rate Limiting<br/>защита от перегрузки]
    end

    Patterns[🎯 Clean Architecture]

    Creational --> Patterns
    Structural --> Patterns
    Behavioral --> Patterns
    Domain --> Patterns
    Resilience --> Patterns

    style Creational fill:#FF6B6B,stroke:#CC5555,stroke-width:2px,color:#fff
    style Structural fill:#4ECDC4,stroke:#3AA39B,stroke-width:2px,color:#000
    style Behavioral fill:#FFE66D,stroke:#D4B942,stroke-width:2px,color:#000
    style Domain fill:#95E1D3,stroke:#6BB0A3,stroke-width:2px,color:#000
    style Resilience fill:#F38181,stroke:#C25A5A,stroke-width:2px,color:#fff
    style Patterns fill:#00E676,stroke:#00C853,stroke-width:4px,color:#000
```

---

## 🎯 Точка зрения: Core Features

### Ключевые возможности системы

```mermaid
mindmap
  root((ИИ-Нутрициолог<br/>Telegram Bot))
    Messaging
      Контекстные диалоги
        История 10 сообщений
        Сохранение контекста
      Роль Нутрициолога
        Промпт из файла
        Специализация в питании
      Команды
        /start - приветствие
        /clear - очистка
        /role - показать роль
        /help - помощь
    Security
      Rate Limiting
        2 секунды между запросами
        Защита от спама
      Валидация
        Макс 4000 символов
        Проверка пустоты
      Error Handling
        Скрытие внутренних ошибок
        Безопасные сообщения
    Performance
      Memory Management
        LRU cache 1000
        TTL 24 часа
        Автоочистка
      Retry Logic
        3 попытки
        Exponential backoff
      Fast Response
        Async архитектура
        Параллельная обработка
    Quality
      Testing
        98 тестов
        71% покрытие
        TDD подход
      Code Quality
        Black форматирование
        Ruff линтер
        Mypy strict
      Architecture
        SOLID принципы
        Clean Architecture
        DI pattern
```

---

## 📈 Точка зрения: Project Metrics

### Метрики проекта

```mermaid
pie title Покрытие тестами по модулям
    "Config (100%)" : 18
    "User (100%)" : 13
    "Conversation (100%)" : 20
    "Handlers (95%)" : 10
    "Metrics (100%)" : 16
    "RoleManager (96%)" : 7
    "Integration (100%)" : 10
    "Validators (94%)" : 7
```

```mermaid
pie title Распределение кода по слоям
    "Domain Logic (40%)" : 40
    "Infrastructure (25%)" : 25
    "Application (20%)" : 20
    "Tests (15%)" : 15
```

```mermaid
pie title Типы тестов
    "Unit Tests (82%)" : 80
    "Integration Tests (18%)" : 18
```

---

## 🚀 Точка зрения: Production Readiness

### Готовность к production

```mermaid
graph LR
    subgraph Functionality["✅ Функциональность"]
        F1[Все команды работают]
        F2[LLM интеграция]
        F3[Управление контекстом]
        F4[Роль Нутрициолога]
    end

    subgraph Security["🔒 Безопасность"]
        S1[Rate limiting ✓]
        S2[Input validation ✓]
        S3[Error hiding ✓]
        S4[No data leaks ✓]
    end

    subgraph Performance["⚡ Производительность"]
        P1[LRU cache ✓]
        P2[TTL cleanup ✓]
        P3[Memory limits ✓]
        P4[Fast response ✓]
    end

    subgraph Reliability["🛡️ Надежность"]
        R1[Retry logic ✓]
        R2[Graceful shutdown ✓]
        R3[Error recovery ✓]
        R4[Logging ✓]
    end

    subgraph Quality["✨ Качество"]
        Q1[98 тестов ✓]
        Q2[71% coverage ✓]
        Q3[Type safety ✓]
        Q4[Clean code ✓]
    end

    subgraph Monitoring["📊 Мониторинг"]
        M1[Метрики ✓]
        M2[Логирование ✓]
        M3[Error tracking ✓]
        M4[Usage stats ✓]
    end

    Production[🎉 PRODUCTION READY<br/>v2.0<br/>Quality Score: 8.7/10]

    Functionality --> Production
    Security --> Production
    Performance --> Production
    Reliability --> Production
    Quality --> Production
    Monitoring --> Production

    style Functionality fill:#66BB6A,stroke:#2E7D32,stroke-width:2px,color:#fff
    style Security fill:#42A5F5,stroke:#1565C0,stroke-width:2px,color:#fff
    style Performance fill:#FFA726,stroke:#F57C00,stroke-width:2px,color:#000
    style Reliability fill:#AB47BC,stroke:#6A1B9A,stroke-width:2px,color:#fff
    style Quality fill:#26C6DA,stroke:#00838F,stroke-width:2px,color:#fff
    style Monitoring fill:#EF5350,stroke:#C62828,stroke-width:2px,color:#fff
    style Production fill:#00E676,stroke:#00C853,stroke-width:5px,color:#000
```

---

## 🎓 Заключение

Этот визуальный гайд представляет проект **Systech AIDD Test** с 12+ различных точек зрения:

1. ✅ **Архитектура** - слоистая структура
2. ✅ **User Journey** - путь пользователя
3. ✅ **Код** - структура модулей
4. ✅ **Data Flow** - поток данных
5. ✅ **Безопасность** - защитные механизмы
6. ✅ **Performance** - управление памятью
7. ✅ **State** - состояния и переходы
8. ✅ **Integration** - API взаимодействия
9. ✅ **SOLID** - принципы проектирования
10. ✅ **Testing** - стратегия тестирования
11. ✅ **Deployment** - процесс развертывания
12. ✅ **Tech Stack** - технологии
13. ✅ **Roles** - система ролей
14. ✅ **Metrics** - мониторинг
15. ✅ **Lifecycle** - жизненный цикл
16. ✅ **Patterns** - паттерны проектирования
17. ✅ **Features** - ключевые возможности
18. ✅ **Metrics** - метрики проекта
19. ✅ **Production** - готовность к продакшену

**Текущее состояние:** Production Ready v2.0 | 98 тестов | 71% покрытие | Quality 8.7/10




