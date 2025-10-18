#!/bin/bash

# =============================================================================
# DEPLOYMENT READINESS CHECK SCRIPT
# =============================================================================
# Скрипт проверяет готовность к развертыванию на production сервере
# 
# Использование: ./devops/deploy-check.sh
# =============================================================================

set -e  # Остановка при ошибке

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Счетчики
PASSED=0
FAILED=0
WARNINGS=0

# Параметры сервера
SERVER_IP="92.255.78.249"
SERVER_USER="systech"
SERVER_DIR="/opt/systech/oleg_h"
SSH_KEY="${SSH_KEY:-$HOME/.ssh/id_rsa_systech}"

# Функции для вывода
print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_check() {
    echo -e "${YELLOW}[CHECK]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓ PASS]${NC} $1"
    ((PASSED++))
}

print_error() {
    echo -e "${RED}[✗ FAIL]${NC} $1"
    ((FAILED++))
}

print_warning() {
    echo -e "${YELLOW}[⚠ WARN]${NC} $1"
    ((WARNINGS++))
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# =============================================================================
# ПРОВЕРКА 1: Локальные файлы
# =============================================================================
print_header "Проверка 1: Наличие необходимых файлов"

# Проверка docker-compose.prod.yml
print_check "Проверка docker-compose.prod.yml..."
if [ -f "docker-compose.prod.yml" ]; then
    print_success "docker-compose.prod.yml найден"
    
    # Проверка портов в конфигурации
    if grep -q "8006:8000" docker-compose.prod.yml; then
        print_success "API порт 8006 настроен корректно"
    else
        print_error "API порт 8006 не настроен (найден другой порт)"
    fi
    
    if grep -q "3006:3000" docker-compose.prod.yml; then
        print_success "Frontend порт 3006 настроен корректно"
    else
        print_error "Frontend порт 3006 не настроен (найден другой порт)"
    fi
else
    print_error "docker-compose.prod.yml не найден"
fi

# Проверка .env файла
print_check "Проверка .env файла..."
if [ -f ".env" ]; then
    print_success ".env файл найден"
    
    # Проверка обязательных переменных
    if grep -q "TELEGRAM_BOT_TOKEN=" .env && ! grep -q "TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here" .env; then
        print_success "TELEGRAM_BOT_TOKEN настроен"
    else
        print_error "TELEGRAM_BOT_TOKEN не настроен или использует значение по умолчанию"
    fi
    
    if grep -q "OPENROUTER_API_KEY=" .env && ! grep -q "OPENROUTER_API_KEY=your_openrouter_api_key_here" .env; then
        print_success "OPENROUTER_API_KEY настроен"
    else
        print_error "OPENROUTER_API_KEY не настроен или использует значение по умолчанию"
    fi
    
    if grep -q "NEXT_PUBLIC_API_URL=" .env; then
        API_URL=$(grep "NEXT_PUBLIC_API_URL=" .env | cut -d '=' -f2)
        if [[ "$API_URL" == *"$SERVER_IP:8006"* ]]; then
            print_success "NEXT_PUBLIC_API_URL настроен для production ($API_URL)"
        else
            print_warning "NEXT_PUBLIC_API_URL: $API_URL (убедитесь, что это правильный URL)"
        fi
    else
        print_error "NEXT_PUBLIC_API_URL не найден в .env"
    fi
else
    print_error ".env файл не найден (скопируйте из env.production.template)"
fi

# Проверка файлов промптов
print_check "Проверка файлов промптов..."
if [ -f "prompts/nutritionist.txt" ]; then
    print_success "prompts/nutritionist.txt найден"
else
    print_error "prompts/nutritionist.txt не найден"
fi

if [ -f "prompts/text2sql.txt" ]; then
    print_success "prompts/text2sql.txt найден"
else
    print_error "prompts/text2sql.txt не найден"
fi

# Проверка миграций
print_check "Проверка файлов миграций Alembic..."
if [ -f "alembic.ini" ]; then
    print_success "alembic.ini найден"
else
    print_error "alembic.ini не найден"
fi

if [ -d "alembic/versions" ] && [ "$(ls -A alembic/versions/*.py 2>/dev/null)" ]; then
    MIGRATION_COUNT=$(ls -1 alembic/versions/*.py 2>/dev/null | wc -l)
    print_success "Найдено миграций: $MIGRATION_COUNT"
else
    print_error "Директория alembic/versions пуста или не существует"
fi

if [ -f "alembic/env.py" ]; then
    print_success "alembic/env.py найден"
else
    print_error "alembic/env.py не найден"
fi

# =============================================================================
# ПРОВЕРКА 2: SSH подключение
# =============================================================================
print_header "Проверка 2: SSH подключение к серверу"

print_check "Проверка SSH ключа..."
if [ -f "$SSH_KEY" ]; then
    print_success "SSH ключ найден: $SSH_KEY"
    
    # Проверка прав доступа
    PERMS=$(stat -c "%a" "$SSH_KEY" 2>/dev/null || stat -f "%A" "$SSH_KEY" 2>/dev/null)
    if [ "$PERMS" == "600" ]; then
        print_success "Права SSH ключа корректны (600)"
    else
        print_warning "Права SSH ключа: $PERMS (рекомендуется 600). Исправить: chmod 600 $SSH_KEY"
    fi
else
    print_error "SSH ключ не найден: $SSH_KEY"
    print_info "Установите путь к ключу: export SSH_KEY=/path/to/your/key"
fi

print_check "Проверка SSH подключения к серверу..."
if [ -f "$SSH_KEY" ]; then
    if ssh -i "$SSH_KEY" -o ConnectTimeout=5 -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" "exit" 2>/dev/null; then
        print_success "SSH подключение успешно"
    else
        print_error "Не удалось подключиться к серверу через SSH"
        print_info "Проверьте: 1) Ключ корректен 2) Сервер доступен 3) Пользователь $SERVER_USER существует"
    fi
else
    print_warning "Пропуск проверки SSH (ключ не найден)"
fi

# =============================================================================
# ПРОВЕРКА 3: Docker на сервере
# =============================================================================
print_header "Проверка 3: Docker на сервере"

if [ -f "$SSH_KEY" ] && ssh -i "$SSH_KEY" -o ConnectTimeout=5 -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" "exit" 2>/dev/null; then
    print_check "Проверка установки Docker..."
    if ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" "docker --version" >/dev/null 2>&1; then
        DOCKER_VERSION=$(ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" "docker --version" 2>/dev/null)
        print_success "Docker установлен: $DOCKER_VERSION"
    else
        print_error "Docker не установлен или недоступен"
    fi
    
    print_check "Проверка установки Docker Compose..."
    if ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" "docker compose version" >/dev/null 2>&1; then
        COMPOSE_VERSION=$(ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" "docker compose version" 2>/dev/null)
        print_success "Docker Compose установлен: $COMPOSE_VERSION"
    else
        print_error "Docker Compose не установлен или недоступен"
    fi
    
    print_check "Проверка прав доступа к Docker..."
    if ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" "docker ps" >/dev/null 2>&1; then
        print_success "Пользователь $SERVER_USER может использовать Docker"
    else
        print_error "Пользователь $SERVER_USER не может использовать Docker (нет прав)"
        print_info "Добавьте пользователя в группу docker: sudo usermod -aG docker $SERVER_USER"
    fi
    
    print_check "Проверка рабочей директории..."
    if ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" "[ -d $SERVER_DIR ]"; then
        print_success "Рабочая директория существует: $SERVER_DIR"
        
        # Проверка прав записи
        if ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" "[ -w $SERVER_DIR ]"; then
            print_success "Есть права на запись в $SERVER_DIR"
        else
            print_error "Нет прав на запись в $SERVER_DIR"
        fi
    else
        print_warning "Рабочая директория не существует: $SERVER_DIR (будет создана)"
    fi
    
    print_check "Проверка занятости портов..."
    # Проверка порта 8006 (API)
    if ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" "netstat -tln 2>/dev/null | grep -q ':8006 '" 2>/dev/null || \
       ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" "ss -tln 2>/dev/null | grep -q ':8006 '" 2>/dev/null; then
        print_warning "Порт 8006 (API) уже используется"
    else
        print_success "Порт 8006 (API) свободен"
    fi
    
    # Проверка порта 3006 (Frontend)
    if ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" "netstat -tln 2>/dev/null | grep -q ':3006 '" 2>/dev/null || \
       ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" "ss -tln 2>/dev/null | grep -q ':3006 '" 2>/dev/null; then
        print_warning "Порт 3006 (Frontend) уже используется"
    else
        print_success "Порт 3006 (Frontend) свободен"
    fi
else
    print_warning "Пропуск проверок на сервере (нет SSH подключения)"
fi

# =============================================================================
# ПРОВЕРКА 4: Docker образы
# =============================================================================
print_header "Проверка 4: Доступность Docker образов"

print_check "Проверка доступности образов в GHCR..."

# Проверка образа bot
if docker manifest inspect ghcr.io/oleg-khalyava/systech-aidd-test-bot:latest >/dev/null 2>&1; then
    print_success "Образ bot:latest доступен"
else
    print_warning "Образ bot:latest недоступен или требуется авторизация"
fi

# Проверка образа api
if docker manifest inspect ghcr.io/oleg-khalyava/systech-aidd-test-api:latest >/dev/null 2>&1; then
    print_success "Образ api:latest доступен"
else
    print_warning "Образ api:latest недоступен или требуется авторизация"
fi

# Проверка образа frontend
if docker manifest inspect ghcr.io/oleg-khalyava/systech-aidd-test-frontend:latest >/dev/null 2>&1; then
    print_success "Образ frontend:latest доступен"
else
    print_warning "Образ frontend:latest недоступен или требуется авторизация"
fi

# =============================================================================
# ИТОГОВЫЙ ОТЧЕТ
# =============================================================================
print_header "Итоговый отчет"

TOTAL=$((PASSED + FAILED + WARNINGS))

echo -e "${GREEN}Успешных проверок: $PASSED${NC}"
echo -e "${RED}Неудачных проверок: $FAILED${NC}"
echo -e "${YELLOW}Предупреждений: $WARNINGS${NC}"
echo -e "Всего проверок: $TOTAL"

echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ Готов к развертыванию!${NC}"
    if [ $WARNINGS -gt 0 ]; then
        echo -e "${YELLOW}Есть предупреждения, но можно продолжить.${NC}"
    fi
    echo ""
    echo -e "${BLUE}Следующие шаги:${NC}"
    echo "1. Следуйте инструкции: devops/doc/guides/manual-deploy.md"
    echo "2. Скопируйте файлы на сервер"
    echo "3. Запустите сервисы"
    exit 0
else
    echo -e "${RED}✗ Обнаружены критические ошибки!${NC}"
    echo -e "${RED}Исправьте ошибки перед развертыванием.${NC}"
    echo ""
    echo -e "${BLUE}Рекомендации:${NC}"
    echo "- Проверьте наличие всех необходимых файлов"
    echo "- Убедитесь, что .env файл заполнен корректно"
    echo "- Проверьте SSH подключение к серверу"
    echo "- Установите Docker и Docker Compose на сервере (если нужно)"
    exit 1
fi

