#!/bin/bash

# Скрипт для сборки и загрузки Docker образа в Yandex Container Registry

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Загружаем переменные из .env
if [ -f .env ]; then
    source .env
else
    echo -e "${RED}❌ Файл .env не найден!${NC}"
    echo "   Создайте его на основе env.example"
    exit 1
fi

# Проверяем наличие необходимых переменных
# YANDEX_REGISTRY_ID может быть как ID registry (crpd50616s9a********), так и name (my-registry)
if [ -z "$YANDEX_REGISTRY_ID" ]; then
    echo -e "${RED}❌ YANDEX_REGISTRY_ID не установлен в .env${NC}"
    echo "   Укажите ID или name registry (можно получить: yc container registry list)"
    exit 1
fi

# Параметры образа
IMAGE_NAME="${IMAGE_NAME:-todoist-bot}"
TAG="${TAG:-latest}"

echo -e "${GREEN}🚀 Начинаем сборку и загрузку образа${NC}"
echo "   Registry identifier: ${YANDEX_REGISTRY_ID}"
echo "   Tag: ${TAG}"
echo ""

# Проверяем авторизацию в Yandex Cloud и получаем ID registry
echo -e "${YELLOW}📋 Проверка авторизации в Yandex Container Registry...${NC}"

# Пытаемся получить registry сначала по name, потом по id
REGISTRY_INFO=$(yc container registry get --name "${YANDEX_REGISTRY_ID}" 2>/dev/null)
if [ $? -ne 0 ]; then
    # Если не получилось по name, пробуем по id
    REGISTRY_INFO=$(yc container registry get --id "${YANDEX_REGISTRY_ID}" 2>/dev/null)
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Ошибка: не удалось получить доступ к registry '${YANDEX_REGISTRY_ID}'${NC}"
        echo ""
        echo "   Убедитесь, что:"
        echo "   1. Установлен Yandex Cloud CLI (yc)"
        echo "   2. Выполнен вход: yc init"
        echo "   3. YANDEX_REGISTRY_ID указан правильно в .env (можно указать как name, так и id)"
        echo ""
        echo "   Для просмотра доступных registry выполните:"
        echo "   yc container registry list"
        exit 1
    fi
fi

# Извлекаем ID registry из вывода
# Формат вывода: id: crpd50616s9a******** или id:crpd50616s9a********
REGISTRY_ID=$(echo "$REGISTRY_INFO" | grep -iE "^id:" | sed 's/^id:\s*//i' | awk '{print $1}')
REGISTRY_NAME=$(echo "$REGISTRY_INFO" | grep -iE "^name:" | sed 's/^name:\s*//i' | awk '{print $1}')

if [ -z "$REGISTRY_ID" ]; then
    echo -e "${RED}❌ Не удалось извлечь ID registry${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Registry найден${NC}"
echo "   Name: ${REGISTRY_NAME:-N/A}"
echo "   ID: ${REGISTRY_ID}"

# Используем ID для формирования URL Docker образа (ID обязателен для URL)
REGISTRY="cr.yandex/${REGISTRY_ID}/${IMAGE_NAME}"
FULL_IMAGE_NAME="${REGISTRY}:${TAG}"
echo "   Docker image: ${FULL_IMAGE_NAME}"
echo ""

# Проверяем, что Docker daemon запущен
echo -e "${YELLOW}🐳 Проверка Docker daemon...${NC}"
if ! docker info &>/dev/null; then
    echo -e "${RED}❌ Docker daemon не запущен!${NC}"
    echo "   Запустите Docker Desktop или Docker daemon"
    echo "   На macOS: откройте Docker Desktop приложение"
    exit 1
fi

# Настраиваем Docker для работы с Yandex Container Registry
echo -e "${YELLOW}🔑 Настройка Docker для работы с Yandex Container Registry...${NC}"
if ! yc container registry configure-docker &>/dev/null; then
    echo -e "${YELLOW}⚠️  Docker уже настроен или произошла ошибка при настройке${NC}"
    echo "   Продолжаем работу..."
fi

# Собираем образ
echo -e "${YELLOW}🔨 Сборка Docker образа...${NC}"
docker build -t "${FULL_IMAGE_NAME}" .

# Также тегируем как latest (если используется другой tag)
if [ "$TAG" != "latest" ]; then
    docker tag "${FULL_IMAGE_NAME}" "${REGISTRY}:latest"
fi

# Загружаем образ в registry
echo -e "${YELLOW}📤 Загрузка образа в Yandex Container Registry...${NC}"
if ! docker push "${FULL_IMAGE_NAME}" 2>&1; then
    echo ""
    echo -e "${RED}❌ Ошибка при загрузке образа в registry${NC}"
    echo ""
    echo "   Возможные причины:"
    echo "   1. Registry ID '${REGISTRY_ID}' не существует или указан неправильно"
    echo "   2. У вас нет прав на push в этот registry"
    echo "   3. Проблемы с авторизацией в Yandex Container Registry"
    echo ""
    echo "   Проверьте:"
    echo "   - Правильность YANDEX_REGISTRY_ID в .env (можно указать как name, так и id)"
    echo "   - Список доступных registry: yc container registry list"
    echo "   - Права доступа к registry: yc container registry get --id '${REGISTRY_ID}'"
    exit 1
fi

if [ "$TAG" != "latest" ]; then
    if ! docker push "${REGISTRY}:latest" 2>&1; then
        echo -e "${YELLOW}⚠️  Не удалось загрузить тег latest, но основной тег загружен${NC}"
    fi
fi

echo ""
echo -e "${GREEN}✅ Образ успешно загружен!${NC}"
echo "   Полное имя образа: ${FULL_IMAGE_NAME}"
echo ""
echo "💡 Для использования в docker-compose.yml:"
echo "   image: ${FULL_IMAGE_NAME}"


