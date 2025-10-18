# Настройка публичных Docker образов в GitHub Packages

## 📦 Введение

По умолчанию GitHub Container Registry (ghcr.io) создает **приватные** образы. Это означает, что для скачивания образов требуется авторизация через токен.

Для публичного доступа (без авторизации) необходимо изменить видимость пакетов на **Public**.

---

## 🎯 Зачем делать образы публичными?

### Преимущества публичных образов:

✅ **Простота использования** - не требуется настройка авторизации  
✅ **Быстрое развертывание** - pull образов без токенов  
✅ **Безлимитные скачивания** - нет ограничений на количество pull  
✅ **Удобство для CI/CD** - проще настраивать автодеплой  
✅ **Open Source friendly** - подходит для публичных проектов

### Недостатки:

⚠️ **Код образа доступен всем** - любой может скачать и проанализировать  
⚠️ **Нет контроля доступа** - невозможно ограничить кто скачивает  

> **Рекомендация:** Используйте публичные образы для open source проектов и демо-приложений. Для коммерческих и приватных проектов оставляйте образы приватными.

---

## 📝 Пошаговая инструкция

### Шаг 1: Убедитесь что образы опубликованы

Сначала необходимо опубликовать образы через GitHub Actions:

```bash
# 1. Закоммитьте изменения
git add .
git commit -m "Add Docker build workflow"

# 2. Push в ветку day-6-devops
git push origin day-6-devops
```

После push GitHub Actions автоматически запустит сборку и публикацию образов.

### Шаг 2: Проверьте статус workflow

1. Откройте ваш репозиторий на GitHub
2. Перейдите в раздел **Actions** (в верхнем меню)
3. Найдите workflow "Build and Push Docker Images"
4. Убедитесь что workflow завершился успешно (✅ зеленый чекбокс)

### Шаг 3: Найдите опубликованные пакеты

1. На главной странице репозитория справа найдите секцию **Packages**
2. Вы должны увидеть 3 пакета:
   - `systech-aidd-test-bot`
   - `systech-aidd-test-api`
   - `systech-aidd-test-frontend`

Если пакеты не отображаются, подождите несколько минут после завершения workflow.

### Шаг 4: Изменение видимости (для каждого образа)

Повторите эти шаги для **каждого** из 3 образов:

#### 4.1. Откройте страницу пакета

1. Кликните на название пакета (например, `systech-aidd-test-bot`)
2. Вы попадете на страницу пакета

#### 4.2. Перейдите в настройки

1. В правой части страницы найдите кнопку **"Package settings"** (шестеренка)
2. Кликните на нее
3. Вы попадете в настройки пакета

#### 4.3. Измените видимость

1. Прокрутите вниз до секции **"Danger Zone"** (красная зона)
2. Найдите пункт **"Change package visibility"**
3. Кликните на кнопку **"Change visibility"**
4. В появившемся диалоге выберите **"Public"**
5. Введите название пакета для подтверждения (например, `systech-aidd-test-bot`)
6. Кликните **"I understand the consequences, change package visibility"**

#### 4.4. Подтверждение

После изменения видимости:
- Статус пакета изменится на **Public** (значок 🌐)
- Образ теперь доступен всем без авторизации

### Шаг 5: Повторите для остальных образов

Повторите Шаг 4 для:
- `systech-aidd-test-api`
- `systech-aidd-test-frontend`

---

## ✅ Проверка публичного доступа

После настройки проверьте что образы доступны без авторизации:

### Тест 1: Pull образа без docker login

```bash
# Без docker login
docker pull ghcr.io/oleg-khalyava/systech-aidd-test-bot:latest
```

**Ожидаемый результат:** Образ успешно скачивается без ошибок авторизации.

### Тест 2: Проверка всех образов

```bash
# Pull всех 3 образов
docker pull ghcr.io/oleg-khalyava/systech-aidd-test-bot:latest
docker pull ghcr.io/oleg-khalyava/systech-aidd-test-api:latest
docker pull ghcr.io/oleg-khalyava/systech-aidd-test-frontend:latest
```

### Тест 3: Запуск через docker-compose.prod.yml

```bash
# Pull и запуск production версии
make docker-prod-pull
make docker-prod-up

# Проверка статуса
docker ps

# Проверка логов
make docker-prod-logs
```

---

## 🔍 Структура пакетов

После успешной публикации и настройки публичного доступа структура выглядит так:

```
GitHub Repository: Oleg-Khalyava/systech-aidd-test
│
├── 📦 Package: systech-aidd-test-bot
│   ├── 🌐 Visibility: Public
│   ├── 🏷️ Tags:
│   │   ├── latest
│   │   └── sha-abc1234
│   └── 📊 Size: ~XXX MB
│
├── 📦 Package: systech-aidd-test-api
│   ├── 🌐 Visibility: Public
│   ├── 🏷️ Tags:
│   │   ├── latest
│   │   └── sha-abc1234
│   └── 📊 Size: ~XXX MB
│
└── 📦 Package: systech-aidd-test-frontend
    ├── 🌐 Visibility: Public
    ├── 🏷️ Tags:
    │   ├── latest
    │   └── sha-abc1234
    └── 📊 Size: ~XXX MB
```

---

## 🔗 Полезные ссылки

### Прямые ссылки на ваши пакеты:

```
https://github.com/Oleg-Khalyava/systech-aidd-test/pkgs/container/systech-aidd-test-bot
https://github.com/Oleg-Khalyava/systech-aidd-test/pkgs/container/systech-aidd-test-api
https://github.com/Oleg-Khalyava/systech-aidd-test/pkgs/container/systech-aidd-test-frontend
```

### Docker pull команды:

```bash
docker pull ghcr.io/oleg-khalyava/systech-aidd-test-bot:latest
docker pull ghcr.io/oleg-khalyava/systech-aidd-test-api:latest
docker pull ghcr.io/oleg-khalyava/systech-aidd-test-frontend:latest
```

---

## ❓ FAQ

### Q: Можно ли вернуть образ обратно в Private?

**A:** Да, в любой момент можно изменить видимость обратно на Private через те же настройки пакета.

### Q: Что делать если пакеты не появляются после push?

**A:** 
1. Проверьте что workflow завершился успешно в разделе Actions
2. Убедитесь что push был в правильную ветку (`day-6-devops`)
3. Проверьте логи workflow на наличие ошибок
4. Подождите 1-2 минуты, иногда пакеты появляются с задержкой

### Q: Нужно ли настраивать что-то еще для публичного доступа?

**A:** Нет, после изменения видимости на Public образы сразу доступны всем. Дополнительная настройка не требуется.

### Q: Можно ли ограничить доступ к конкретным тегам?

**A:** Нет, видимость (Public/Private) применяется ко всему пакету целиком, а не к отдельным тегам.

### Q: Что делать если при pull образа требуется авторизация?

**A:** 
1. Проверьте что видимость пакета установлена в Public (см. Шаг 4)
2. Убедитесь что вы используете правильный путь к образу
3. Попробуйте сделать `docker logout ghcr.io` и повторить pull

---

## 📚 Дополнительная информация

- [GitHub Packages Documentation](https://docs.github.com/en/packages)
- [Working with Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Publishing Docker Images](https://docs.github.com/en/actions/publishing-packages/publishing-docker-images)

---

**Готово!** Теперь ваши Docker образы публичные и доступны для использования всем без авторизации. 🎉

