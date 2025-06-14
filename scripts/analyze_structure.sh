#!/bin/bash
# Скрипт для анализа текущей структуры директорий
# Путь: /Users/alexeymakrushin/Yandex.Disk.localized/makrushindisk/Projects/RAG/scripts/sync/analyze_structure.sh

# Цветной вывод для лучшей читаемости
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Директория для анализа
DISK_DIR="/Users/alexeymakrushin/Yandex.Disk.localized/makrushindisk"
OUTPUT_FILE="/Users/alexeymakrushin/Yandex.Disk.localized/makrushindisk/Projects/RAG/docs/storage_structure_analysis.md"

echo -e "${GREEN}Анализ текущей структуры директории ${DISK_DIR}${NC}"
echo -e "${BLUE}===========================================${NC}"

# Создание директории для отчета, если она не существует
mkdir -p "$(dirname "$OUTPUT_FILE")"

# Создаем отчет в markdown формате
echo "# Анализ структуры директории для RAG-проекта" > $OUTPUT_FILE
echo "" >> $OUTPUT_FILE
echo "## Дата анализа: $(date '+%Y-%m-%d %H:%M:%S')" >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE

# Анализ директории
echo -e "${YELLOW}Анализ директории: ${DISK_DIR}${NC}"

if [ ! -d "$DISK_DIR" ]; then
    echo -e "${RED}Директория не существует: ${DISK_DIR}${NC}"
    echo "Директория не найдена: \`$DISK_DIR\`" >> $OUTPUT_FILE
    exit 1
fi

# Получение общего размера директории
size=$(du -sh "$DISK_DIR" | cut -f1)

# Получение количества файлов
file_count=$(find "$DISK_DIR" -type f | wc -l)

# Получение типов файлов (топ 10 расширений)
file_types=$(find "$DISK_DIR" -type f -name "*.*" | grep -o '\.[^\.]*$' | sort | uniq -c | sort -nr | head -10)

# Получение структуры директорий (только первый уровень)
subdirs=$(find "$DISK_DIR" -maxdepth 1 -type d | sort)

# Запись в отчет
echo "## Основная информация" >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE
echo "**Путь:** \`$DISK_DIR\`" >> $OUTPUT_FILE
echo "**Общий размер:** $size" >> $OUTPUT_FILE
echo "**Количество файлов:** $file_count" >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE

echo "## Наиболее распространенные типы файлов:" >> $OUTPUT_FILE
echo "```" >> $OUTPUT_FILE
echo "$file_types" >> $OUTPUT_FILE
echo "```" >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE

echo "## Структура директорий (первый уровень):" >> $OUTPUT_FILE
echo "```" >> $OUTPUT_FILE
for subdir in $subdirs; do
    if [ "$subdir" != "$DISK_DIR" ]; then
        subdir_size=$(du -sh "$subdir" 2>/dev/null | cut -f1)
        echo "$(basename "$subdir") - $subdir_size" >> $OUTPUT_FILE
    fi
done
echo "```" >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE

# Анализ структуры второго уровня для важных директорий
echo "## Структура важных поддиректорий:" >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE

# Функция для анализа директории второго уровня
analyze_subdir() {
    local dir_path="$1"
    local dir_name="$(basename "$dir_path")"
    
    echo "### $dir_name" >> $OUTPUT_FILE
    echo "" >> $OUTPUT_FILE
    
    local subdir_size=$(du -sh "$dir_path" 2>/dev/null | cut -f1)
    local subdir_files=$(find "$dir_path" -type f | wc -l)
    
    echo "**Размер:** $subdir_size" >> $OUTPUT_FILE
    echo "**Количество файлов:** $subdir_files" >> $OUTPUT_FILE
    echo "" >> $OUTPUT_FILE
    
    echo "#### Содержимое директории:" >> $OUTPUT_FILE
    echo "```" >> $OUTPUT_FILE
    local sub_subdirs=$(find "$dir_path" -maxdepth 1 -type d | sort)
    for sub_subdir in $sub_subdirs; do
        if [ "$sub_subdir" != "$dir_path" ]; then
            local sub_subdir_size=$(du -sh "$sub_subdir" 2>/dev/null | cut -f1)
            echo "$(basename "$sub_subdir") - $sub_subdir_size" >> $OUTPUT_FILE
        fi
    done
    echo "```" >> $OUTPUT_FILE
    echo "" >> $OUTPUT_FILE
}

# Анализируем некоторые важные директории (первые 5)
count=0
for subdir in $subdirs; do
    if [ "$subdir" != "$DISK_DIR" ] && [ $count -lt 5 ]; then
        analyze_subdir "$subdir"
        count=$((count+1))
    fi
done

# Добавление рекомендаций в отчет
echo "## Рекомендации для синхронизации" >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE
echo "На основе анализа структуры директории, рекомендуется следующая стратегия синхронизации:" >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE
echo "1. **makrushindisk → Google Drive**: Настроить одностороннюю синхронизацию, чтобы создать копию всех файлов на Google Drive" >> $OUTPUT_FILE
echo "2. **makrushindisk → NAS**: Настроить двустороннюю синхронизацию для обеспечения резервного копирования и доступа с сервера" >> $OUTPUT_FILE
echo "3. **makrushinrag**: Создать отдельную директорию для RAG системы на сервере с копией на Google Drive для интеграции с AI" >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE

echo -e "${GREEN}Анализ завершен. Отчет сохранен в: ${OUTPUT_FILE}${NC}"
echo ""
echo -e "${BLUE}Основная информация:${NC}"
echo -e "${GREEN}Размер директории:${NC} $size"
echo -e "${GREEN}Количество файлов:${NC} $file_count"
