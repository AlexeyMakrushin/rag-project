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
