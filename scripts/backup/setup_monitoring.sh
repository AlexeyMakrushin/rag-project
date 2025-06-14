#!/bin/bash
# setup_monitoring.sh - Скрипт для настройки мониторинга и логирования

# Проверка запуска от root
if [ "$(id -u)" != "0" ]; then
   echo "Этот скрипт должен быть запущен с правами root" 1>&2
   exit 1
fi

echo "Начинаем настройку мониторинга и логирования..."

# Определение корневого каталога проекта
PROJECT_ROOT="/home/raguser/rag-project"

# Установка необходимых пакетов для мониторинга
echo "Установка необходимых пакетов..."
apt update
apt install -y logrotate bc sysstat

# Настройка logrotate для ротации логов проекта
echo "Настройка logrotate..."
cat > /etc/logrotate.d/rag-project << EOF
$PROJECT_ROOT/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 640 raguser raguser
    sharedscripts
    postrotate
        systemctl reload rsyslog >/dev/null 2>&1 || true
    endscript
}
EOF

# Создание скрипта для мониторинга системных ресурсов
echo "Создание скрипта мониторинга системных ресурсов..."
cat > $PROJECT_ROOT/scripts/monitor_system.sh << 'EOF'
#!/bin/bash
# Скрипт для мониторинга системных ресурсов

# Путь к папке логов
LOG_DIR="/home/raguser/rag-project/logs"
LOG_FILE="$LOG_DIR/system_monitor.log"
ALERT_FILE="$LOG_DIR/alerts.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

# Создание записи в лог
log_message() {
    echo "$DATE - $1" >> $LOG_FILE
}

# Создание предупреждения
log_alert() {
    echo "$DATE - ALERT: $1" >> $ALERT_FILE
    echo "$DATE - ALERT: $1" >> $LOG_FILE
}

# Проверка использования CPU
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2 + $4}')
log_message "CPU Usage: $CPU_USAGE%"

# Проверка использования RAM
TOTAL_RAM=$(free -m | awk '/^Mem:/{print $2}')
USED_RAM=$(free -m | awk '/^Mem:/{print $3}')
RAM_PERCENTAGE=$(echo "scale=2; $USED_RAM*100/$TOTAL_RAM" | bc)
log_message "Memory Usage: $USED_RAM MB / $TOTAL_RAM MB ($RAM_PERCENTAGE%)"

# Проверка использования дисков
DISK_USAGE=$(df -h / | awk 'NR==2{print $5}' | tr -d '%')
DISK_AVAIL=$(df -h / | awk 'NR==2{print $4}')
log_message "Disk Usage: $DISK_USAGE% (Available: $DISK_AVAIL)"

# Проверка загрузки системы
LOAD=$(uptime | awk -F'[a-z]:' '{ print $2}' | awk '{print $1}' | tr -d ',')
log_message "System Load: $LOAD"

# Проверка активных подключений
CONNECTIONS=$(netstat -tun | grep ESTABLISHED | wc -l)
log_message "Active Connections: $CONNECTIONS"

# Проверка Docker контейнеров
DOCKER_RUNNING=$(docker ps -q | wc -l)
DOCKER_TOTAL=$(docker ps -a -q | wc -l)
log_message "Docker Containers: $DOCKER_RUNNING running / $DOCKER_TOTAL total"

# Проверка свободной памяти для Docker
DOCKER_MEMORY=$(docker stats --no-stream --format "{{.MemPerc}}" | tr -d '%' | awk '{s+=$1} END {print s}')
if [[ ! -z "$DOCKER_MEMORY" ]]; then
    log_message "Docker Memory Usage: $DOCKER_MEMORY%"
fi

# Отправка предупреждений, если использование ресурсов превышает пороги
if (( $(echo "$CPU_USAGE > 80" | bc -l) )); then
    log_alert "High CPU usage: $CPU_USAGE%"
fi

if (( $(echo "$RAM_PERCENTAGE > 80" | bc -l) )); then
    log_alert "High memory usage: $RAM_PERCENTAGE%"
fi

if (( $DISK_USAGE > 80 )); then
    log_alert "High disk usage: $DISK_USAGE%"
fi

if (( $(echo "$LOAD > 4" | bc -l) )); then
    log_alert "High system load: $LOAD"
fi

# Сформировать отчет в HTML
HTML_REPORT="$LOG_DIR/system_report.html"
cat > $HTML_REPORT << HTML
<!DOCTYPE html>
<html>
<head>
    <title>System Monitoring Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #333; }
        .stats { margin: 20px 0; }
        .stats table { border-collapse: collapse; width: 100%; }
        .stats th, .stats td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        .stats th { background-color: #f2f2f2; }
        .warning { color: orange; }
        .critical { color: red; }
        .normal { color: green; }
    </style>
</head>
<body>
    <h1>System Monitoring Report</h1>
    <p>Generated on: $DATE</p>
    
    <div class="stats">
        <h2>System Resources</h2>
        <table>
            <tr>
                <th>Metric</th>
                <th>Value</th>
                <th>Status</th>
            </tr>
            <tr>
                <td>CPU Usage</td>
                <td>$CPU_USAGE%</td>
                <td class="$([ $(echo "$CPU_USAGE > 80" | bc -l) -eq 1 ] && echo 'critical' || [ $(echo "$CPU_USAGE > 60" | bc -l) -eq 1 ] && echo 'warning' || echo 'normal')">
                    $([ $(echo "$CPU_USAGE > 80" | bc -l) -eq 1 ] && echo 'CRITICAL' || [ $(echo "$CPU_USAGE > 60" | bc -l) -eq 1 ] && echo 'WARNING' || echo 'OK')
                </td>
            </tr>
            <tr>
                <td>Memory Usage</td>
                <td>$RAM_PERCENTAGE% ($USED_RAM MB / $TOTAL_RAM MB)</td>
                <td class="$([ $(echo "$RAM_PERCENTAGE > 80" | bc -l) -eq 1 ] && echo 'critical' || [ $(echo "$RAM_PERCENTAGE > 60" | bc -l) -eq 1 ] && echo 'warning' || echo 'normal')">
                    $([ $(echo "$RAM_PERCENTAGE > 80" | bc -l) -eq 1 ] && echo 'CRITICAL' || [ $(echo "$RAM_PERCENTAGE > 60" | bc -l) -eq 1 ] && echo 'WARNING' || echo 'OK')
                </td>
            </tr>
            <tr>
                <td>Disk Usage</td>
                <td>$DISK_USAGE% (Available: $DISK_AVAIL)</td>
                <td class="$([ $DISK_USAGE -gt 80 ] && echo 'critical' || [ $DISK_USAGE -gt 60 ] && echo 'warning' || echo 'normal')">
                    $([ $DISK_USAGE -gt 80 ] && echo 'CRITICAL' || [ $DISK_USAGE -gt 60 ] && echo 'WARNING' || echo 'OK')
                </td>
            </tr>
            <tr>
                <td>System Load</td>
                <td>$LOAD</td>
                <td class="$([ $(echo "$LOAD > 4" | bc -l) -eq 1 ] && echo 'critical' || [ $(echo "$LOAD > 2" | bc -l) -eq 1 ] && echo 'warning' || echo 'normal')">
                    $([ $(echo "$LOAD > 4" | bc -l) -eq 1 ] && echo 'CRITICAL' || [ $(echo "$LOAD > 2" | bc -l) -eq 1 ] && echo 'WARNING' || echo 'OK')
                </td>
            </tr>
        </table>
    </div>
    
    <div class="stats">
        <h2>Network & Docker</h2>
        <table>
            <tr>
                <th>Metric</th>
                <th>Value</th>
            </tr>
            <tr>
                <td>Active Connections</td>
                <td>$CONNECTIONS</td>
            </tr>
            <tr>
                <td>Docker Containers</td>
                <td>$DOCKER_RUNNING running / $DOCKER_TOTAL total</td>
            </tr>
            <tr>
                <td>Docker Memory Usage</td>
                <td>$DOCKER_MEMORY%</td>
            </tr>
        </table>
    </div>
</body>
</html>
HTML

echo "System monitoring completed at $DATE"
EOF

# Создание скрипта для проверки здоровья сервисов
echo "Создание скрипта для проверки здоровья сервисов..."
cat > $PROJECT_ROOT/scripts/health_check.sh << 'EOF'
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
EOF

# Настройка cron для запуска мониторинга и проверок здоровья
echo "Настройка cron для периодического мониторинга..."
(crontab -l 2>/dev/null || echo "") | grep -v "monitor_system.sh\|health_check.sh" | cat - > /tmp/crontab.new
echo "*/5 * * * * $PROJECT_ROOT/scripts/monitor_system.sh >/dev/null 2>&1" >> /tmp/crontab.new
echo "*/10 * * * * $PROJECT_ROOT/scripts/health_check.sh >/dev/null 2>&1" >> /tmp/crontab.new
crontab /tmp/crontab.new
rm /tmp/crontab.new

# Настройка прав доступа
echo "Настройка прав доступа..."
chmod +x $PROJECT_ROOT/scripts/monitor_system.sh
chmod +x $PROJECT_ROOT/scripts/health_check.sh
chown raguser:raguser $PROJECT_ROOT/scripts/monitor_system.sh
chown raguser:raguser $PROJECT_ROOT/scripts/health_check.sh

echo "Настройка мониторинга и логирования завершена!"
echo "Мониторинг системы будет запускаться каждые 5 минут"
echo "Проверка здоровья сервисов будет запускаться каждые 10 минут"
echo "Логи будут ротироваться ежедневно и храниться в сжатом виде в течение 14 дней"
