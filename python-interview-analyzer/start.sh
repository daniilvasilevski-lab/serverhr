#!/bin/bash

# ===================================================================
# STARTUP SCRIPT FOR INTERVIEW ANALYZER
# ===================================================================
# Этот скрипт проверяет окружение и запускает приложение
# ===================================================================

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║       INTERVIEW ANALYZER - STARTUP CHECK                   ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Функция для проверок
check_step() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $1"
    else
        echo -e "${RED}✗${NC} $1"
        exit 1
    fi
}

# 1. Проверка Python версии
echo -e "\n${YELLOW}[1/8]${NC} Checking Python version..."
python_version=$(python --version 2>&1 | awk '{print $2}')
required_version="3.11"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then
    check_step "Python $python_version (required >= $required_version)"
else
    echo -e "${RED}✗${NC} Python version $python_version is too old (required >= $required_version)"
    exit 1
fi

# 2. Проверка .env файла
echo -e "\n${YELLOW}[2/8]${NC} Checking .env file..."
if [ -f ".env" ]; then
    check_step ".env file exists"
else
    echo -e "${RED}✗${NC} .env file not found!"
    echo -e "${YELLOW}Creating .env from .env.example...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Please edit .env file and add your OPENAI_API_KEY${NC}"
    exit 1
fi

# 3. Проверка OPENAI_API_KEY
echo -e "\n${YELLOW}[3/8]${NC} Checking OpenAI API key..."
source .env
if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "sk-your-openai-api-key-here" ]; then
    echo -e "${RED}✗${NC} OPENAI_API_KEY not configured in .env"
    exit 1
fi
check_step "OPENAI_API_KEY is configured"

# 4. Проверка prompts.yaml
echo -e "\n${YELLOW}[4/8]${NC} Checking prompts.yaml..."
if [ -f "prompts.yaml" ]; then
    check_step "prompts.yaml file exists"
else
    echo -e "${YELLOW}⚠️${NC}  prompts.yaml not found, will use defaults"
fi

# 5. Проверка Google Sheets credentials (optional)
echo -e "\n${YELLOW}[5/8]${NC} Checking Google Sheets integration..."
if [ ! -z "$GOOGLE_SERVICE_ACCOUNT_KEY" ] && [ -f "$GOOGLE_SERVICE_ACCOUNT_KEY" ]; then
    check_step "Google Sheets credentials configured"
elif [ ! -z "$SOURCE_SHEET_URL" ]; then
    echo -e "${YELLOW}⚠️${NC}  Google Sheets URLs configured but credentials missing"
else
    echo -e "${YELLOW}ℹ️${NC}  Google Sheets integration not configured (optional)"
fi

# 6. Создание необходимых директорий
echo -e "\n${YELLOW}[6/8]${NC} Creating directories..."
mkdir -p logs temp data credentials
check_step "Directories created"

# 7. Проверка портов
echo -e "\n${YELLOW}[7/8]${NC} Checking port availability..."
PORT=${PORT:-8000}
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${YELLOW}⚠️${NC}  Port $PORT is already in use"
    echo -e "${YELLOW}   Run: kill \$(lsof -t -i:$PORT) to free the port${NC}"
else
    check_step "Port $PORT is available"
fi

# 8. Проверка зависимостей
echo -e "\n${YELLOW}[8/8]${NC} Checking dependencies..."
if python -c "import fastapi, openai, yaml" 2>/dev/null; then
    check_step "Core dependencies installed"
else
    echo -e "${RED}✗${NC} Some dependencies are missing"
    echo -e "${YELLOW}Installing dependencies...${NC}"
    pip install -r requirements.txt
    check_step "Dependencies installed"
fi

# Итоговая информация
echo -e "\n${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ All checks passed!${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"

echo -e "\n${BLUE}Configuration:${NC}"
echo -e "  Environment: ${GREEN}${ENV:-development}${NC}"
echo -e "  Port: ${GREEN}${PORT:-8000}${NC}"
echo -e "  Log Level: ${GREEN}${LOG_LEVEL:-INFO}${NC}"
echo -e "  OpenAI API: ${GREEN}✓ Configured${NC}"

if [ ! -z "$SOURCE_SHEET_URL" ]; then
    echo -e "  Google Sheets: ${GREEN}✓ Configured${NC}"
else
    echo -e "  Google Sheets: ${YELLOW}⚠ Not configured${NC}"
fi

echo -e "\n${BLUE}Starting server on http://0.0.0.0:${PORT:-8000}${NC}"
echo -e "${BLUE}API Documentation: http://localhost:${PORT:-8000}/docs${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}\n"

# Запуск приложения
exec uvicorn app.main:app --host ${HOST:-0.0.0.0} --port ${PORT:-8000} --reload
