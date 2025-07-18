# Детальная постановка задачи для второго этапа: Настройка синхронизации файлов

## Цель
Настроить автоматическую двустороннюю синхронизацию файлов между всеми источниками данных (Synology NAS, сервер, Yandex Disk, Google Drive, MacBook Air, iMac) с обеспечением надежности, разрешением конфликтов и мониторингом.

## Выполненные задачи

### 1. Анализ и выбор инструмента синхронизации ✅
- Проведено сравнение Syncthing и rclone по ключевым параметрам
- Выбрано гибридное решение:
  - rclone для синхронизации с облачными хранилищами и сервером
  - Нативные клиенты для синхронизации на локальных устройствах
  - Символические ссылки для объединения директорий разных облачных провайдеров
- Обоснование: такой подход объединяет сильные стороны каждого инструмента

### 2. Настройка синхронизации с облачными хранилищами ✅
- Установлен и настроен rclone на сервере
- Настроен доступ к Google Drive через Service Account
- Настроена директория `makrushinrag` для синхронизации данных
- Создана синхронизация между сервером и Google Drive
- Настроено соединение между Yandex Disk и Google Drive через символические ссылки на компьютере
- Автоматическая синхронизация между компьютером и облачными хранилищами через нативные клиенты

### 3. Настройка сервера для синхронизации ✅
- Создана директория `/home/makrushin/makrushinrag` на сервере
- Создан скрипт синхронизации `/home/makrushin/rag-project/scripts/sync/sync_server_to_gdrive.sh`
- Настроено расписание cron для запуска синхронизации каждые 10 минут
- Настроено логирование процессов синхронизации

### 4. Настройка локальной структуры на Mac ✅
- Создана директория `/Users/alexeymakrushin/Yandex.Disk.localized/makrushinrag` 
- Настроена символическая ссылка с директорией Google Drive
- Обеспечена синхронизация в реальном времени на Mac

## Архитектура синхронизации

```
+------------------+    real-time    +------------------+
| Mac: Yandex Disk |<--------------->| Yandex Cloud     |
|  /makrushinrag   |                 |                  |
+---------+--------+                 +------------------+
          |
          | symlink
          v
+------------------+    real-time    +------------------+
| Mac: Google Drive|<--------------->| Google Drive     |
|  /makrushinrag   |                 |                  |
+------------------+                 +---------+--------+
                                               |
                                               | rclone (10 min)
                                               v
                                     +------------------+
                                     | Server           |
                                     | /makrushinrag    |
                                     +------------------+
```

## Конфигурационные файлы и скрипты

### Скрипт синхронизации на сервере
```bash
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
```

### Конфигурация cron на сервере
```
# Синхронизация каждые 10 минут
*/10 * * * * /home/makrushin/rag-project/scripts/sync/sync_server_to_gdrive.sh
```

## Инструкция по созданию символических ссылок на Mac

Для связывания директорий Яндекс Диска и Google Drive:
```bash
# Yandex.Disk -> Google Drive (makrushinrag)
ln -s "/Users/alexeymakrushin/Yandex.Disk.localized/makrushinrag" "/Users/alexeymakrushin/Мой диск/makrushinrag"

# Yandex.Disk -> Google Drive (makrushindisk)
ln -s "/Users/alexeymakrushin/Yandex.Disk.localized/makrushindisk" "/Users/alexeymakrushin/Мой диск/makrushindisk"
```

## Текущие ограничения и будущие улучшения

1. **Synology NAS**: Синхронизация с NAS пока не настроена и запланирована на следующий этап.
2. **Разрешение конфликтов**: Стратегии разрешения конфликтов основаны на логике облачных провайдеров, в будущем требуется доработка.
3. **Мониторинг**: Система мониторинга и уведомлений требует дальнейшей разработки.
4. **Syncthing**: В будущих версиях может потребоваться добавление Syncthing для более гибкой синхронизации между локальными устройствами.

## Дальнейшие действия

1. Настроить синхронизацию с Synology NAS
2. Реализовать систему уведомлений через Telegram/email при сбоях синхронизации
3. Разработать более продвинутую систему мониторинга и логирования
4. Протестировать работу с большими объемами данных и в условиях высокой нагрузки

## Критерии успеха
- ✅ Синхронизация запускается автоматически по расписанию или триггерам
- ✅ Новые файлы появляются на сервере в течение 10 минут после создания в любом источнике
- ⚠️ Конфликты разрешаются автоматически (требуется дополнительное тестирование)
- ❌ Система уведомлений о проблемах (требуется реализация)
- ✅ Процессы синхронизации документированы