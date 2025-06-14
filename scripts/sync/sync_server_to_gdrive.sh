#!/bin/bash
# Скрипт для синхронизации данных между сервером и Google Drive

# Цветной вывод для лучшей читаемости
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Директории для синхронизации
LOCAL_DIR="/home/makrushin/makrushinrag"
REMOTE_DIR="googledrive:"
LOG_FILE="/home/makrushin/rag-project/logs/sync_server_gdrive.log"

# Создание директорий для логов и синхронизации, если они не существуют
mkdir -p "$(dirname "$LOG_FILE")"
mkdir -p "$LOCAL_DIR"

# Timestamp для записи в лог
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

echo -e "${BLUE}$TIMESTAMP - Запуск синхронизации сервер <-> Google Drive${NC}" | tee -a "$LOG_FILE"

# Синхронизация с сервера на Google Drive
echo -e "${YELLOW}Синхронизация данных с сервера на Google Drive...${NC}" | tee -a "$LOG_FILE"
if rclone sync "$LOCAL_DIR" "$REMOTE_DIR" --progress --create-empty-src-dirs 2>> "$LOG_FILE"; then
    echo -e "${GREEN}Синхронизация сервер -> Google Drive завершена успешно${NC}" | tee -a "$LOG_FILE"
else
    echo -e "${RED}Ошибка при синхронизации сервер -> Google Drive${NC}" | tee -a "$LOG_FILE"
fi

# Синхронизация с Google Drive на сервер
echo -e "${YELLOW}Синхронизация данных с Google Drive на сервер...${NC}" | tee -a "$LOG_FILE"
if rclone sync "$REMOTE_DIR" "$LOCAL_DIR" --progress --create-empty-src-dirs 2>> "$LOG_FILE"; then
    echo -e "${GREEN}Синхронизация Google Drive -> сервер завершена успешно${NC}" | tee -a "$LOG_FILE"
else
    echo -e "${RED}Ошибка при синхронизации Google Drive -> сервер${NC}" | tee -a "$LOG_FILE"
fi

# Запись в лог о завершении
echo -e "${BLUE}$TIMESTAMP - Синхронизация завершена${NC}" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
