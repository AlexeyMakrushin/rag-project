#!/bin/bash
# Скрипт для проверки здоровья сервисов

# Путь к папке логов
LOG_DIR="/home/raguser/rag-project/logs"
LOG_FILE="$LOG_DIR/health_check.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

# Создание записи в лог
log_message() {
    echo "$DATE - $1" >> $LOG_FILE
}

# Создание предупреждения
log_alert() {
    echo "$DATE - ALERT: $1" >> $LOG_FILE
}

# Проверка доступности Docker
if ! docker info >/dev/null 2>&1; then
    log_alert "Docker daemon is not running!"
else
    log_message "Docker daemon is running"
    
    # Проверка запущенных контейнеров
    docker ps -a | grep -v "CONTAINER ID" | while read line; do
        CONTAINER_ID=$(echo $line | awk '{print $1}')
        CONTAINER_NAME=$(echo $line | awk '{print $(NF)}')
        CONTAINER_STATUS=$(docker inspect --format='{{.State.Status}}' $CONTAINER_ID)
        
        if [ "$CONTAINER_STATUS" != "running" ]; then
            log_alert "Container $CONTAINER_NAME is not running. Status: $CONTAINER_STATUS"
        else
            HEALTH_STATUS=$(docker inspect --format='{{if .State.Health}}{{.State.Health.Status}}{{else}}no health check{{end}}' $CONTAINER_ID)
            log_message "Container $CONTAINER_NAME status: $CONTAINER_STATUS, health: $HEALTH_STATUS"
        fi
    done
fi

# Проверка наличия файлов логов
for LOG_FILE in sync.log ingest.log embed.log api.log; do
    if [ ! -f "$LOG_DIR/$LOG_FILE" ]; then
        log_alert "Log file $LOG_FILE does not exist!"
    else
        # Проверка на наличие ошибок в логах
        ERROR_COUNT=$(grep -i "error\|exception\|fatal" "$LOG_DIR/$LOG_FILE" | wc -l)
        if [ $ERROR_COUNT -gt 0 ]; then
            log_alert "Found $ERROR_COUNT errors in $LOG_FILE"
        else
            log_message "No errors found in $LOG_FILE"
        fi
    fi
done

echo "Health check completed at $DATE"
