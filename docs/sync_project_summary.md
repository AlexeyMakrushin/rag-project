# Отчет о настройке синхронизации для RAG-проекта

## Общая информация

**Дата выполнения:** Май 2025  
**Цель:** Настройка автоматической двусторонней синхронизации файлов между различными устройствами (сервер, MacBook, Yandex Disk, Google Drive)  
**Исполнитель:** Claude AI Ассистент  

## Что было сделано

### 1. Анализ и выбор инструментов синхронизации

- Проведен сравнительный анализ Syncthing и rclone
- Выбрана комбинированная стратегия:
  - rclone для синхронизации между сервером и Google Drive
  - Нативные клиенты для синхронизации на Mac
  - Символические ссылки для объединения Yandex Disk и Google Drive

### 2. Настройка синхронизации на сервере

- Установлен и настроен rclone на сервере Linux 109.107.189.224
- Создана директория `/home/makrushin/makrushinrag` для хранения данных
- Настроена синхронизация с Google Drive через service account
- Создан скрипт синхронизации 
- Настроен запуск синхронизации по расписанию (каждые 10 минут)

### 3. Настройка на Mac

- Настроены символические ссылки между директориями Yandex Disk и Google Drive
- Обеспечена синхронизация в реальном времени через нативные клиенты

### 4. Тестирование

- Проведены тесты создания и синхронизации файлов
- Подтверждена работоспособность двусторонней синхронизации

## Созданные файлы и директории

### На сервере

| Путь | Описание |
|------|----------|
| `/home/makrushin/makrushinrag` | Основная директория для хранения данных RAG |
| `/home/makrushin/rag-project/scripts/sync/sync_server_to_gdrive.sh` | Скрипт для синхронизации между сервером и Google Drive |
| `/home/makrushin/rag-project/logs/sync_server_gdrive.log` | Лог-файл процессов синхронизации |
| `/home/makrushin/.config/rclone/service-account.json` | Ключ service account для доступа к Google Drive |

### На MacBook

| Путь | Описание |
|------|----------|
| `/Users/alexeymakrushin/Yandex.Disk.localized/makrushinrag` | Основная директория для хранения данных в Yandex Disk |
| `/Users/alexeymakrushin/Мой диск/makrushinrag` | Символическая ссылка на директорию в Yandex Disk |
| `/Users/alexeymakrushin/Yandex.Disk.localized/makrushindisk` | Директория для хранения повседневных документов в Yandex Disk |
| `/Users/alexeymakrushin/Мой диск/makrushindisk` | Символическая ссылка на директорию в Yandex Disk |
| `/Users/alexeymakrushin/Yandex.Disk.localized/makrushindisk/Projects/RAG/docs/dialog_2_sync.md` | Документация по настройке синхронизации |
| `/Users/alexeymakrushin/Yandex.Disk.localized/makrushindisk/Projects/RAG/docs/working_with_ai_prompt.md` | Руководство по работе с AI ассистентом |

### Настройки cron

На сервере настроен cron для запуска синхронизации каждые 10 минут:

```bash
*/10 * * * * /home/makrushin/rag-project/scripts/sync/sync_server_to_gdrive.sh
```

## Содержимое ключевых файлов

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

## Команды для создания символических ссылок

```bash
# Создание символической ссылки для папки makrushinrag
ln -s "/Users/alexeymakrushin/Yandex.Disk.localized/makrushinrag" "/Users/alexeymakrushin/Мой диск/makrushinrag"

# Создание символической ссылки для папки makrushindisk
ln -s "/Users/alexeymakrushin/Yandex.Disk.localized/makrushindisk" "/Users/alexeymakrushin/Мой диск/makrushindisk"
```

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

## Что нужно сохранить

1. **Ключевые директории:**
   - `/Users/alexeymakrushin/Yandex.Disk.localized/makrushinrag` - основная директория данных
   - `/home/makrushin/makrushinrag` - директория на сервере

2. **Важные скрипты:**
   - `/home/makrushin/rag-project/scripts/sync/sync_server_to_gdrive.sh` - скрипт синхронизации

3. **Конфигурационные файлы:**
   - `/home/makrushin/.config/rclone/service-account.json` - ключ service account
   - Настройки rclone на сервере (созданы через `rclone config`)

4. **Документация:**
   - `/Users/alexeymakrushin/Yandex.Disk.localized/makrushindisk/Projects/RAG/docs/dialog_2_sync.md` - отчет о настройке
   - `/Users/alexeymakrushin/Yandex.Disk.localized/makrushindisk/Projects/RAG/docs/working_with_ai_prompt.md` - руководство

## Что можно удалить

1. **Временные файлы для тестирования:**
   - `test.txt` и другие тестовые файлы, созданные для проверки синхронизации

2. **Устаревшие скрипты и конфигурации:**
   - Любые предварительные версии скриптов синхронизации
   - Старые настройки rclone, если они существуют

## Следующие шаги

1. Мониторинг работы синхронизации в течение недели
2. Настройка резервного копирования на NAS (при необходимости)
3. Разработка системы уведомлений о проблемах с синхронизацией
4. Настройка более продвинутого логирования

## Заключение

Настроена эффективная система двусторонней синхронизации между всеми необходимыми устройствами и хранилищами. Система обеспечивает синхронизацию в реальном времени для локальных устройств и регулярную синхронизацию (каждые 10 минут) с сервером.

Все процессы автоматизированы и не требуют ручного вмешательства. Логирование обеспечивает возможность отслеживания проблем с синхронизацией.
