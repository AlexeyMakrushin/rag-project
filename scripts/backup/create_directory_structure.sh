#!/bin/bash
# create_directory_structure.sh - Скрипт для создания структуры каталогов проекта

# Проверка запуска от пользователя raguser
if [ "$(whoami)" != "raguser" ] && [ "$(whoami)" != "root" ]; then
   echo "Этот скрипт должен быть запущен от пользователя raguser или root" 1>&2
   exit 1
fi

echo "Начинаем создание структуры каталогов проекта..."

# Определение корневого каталога проекта
PROJECT_ROOT="/home/raguser/rag-project"

# Создание основной структуры каталогов
echo "Создание основных каталогов..."
mkdir -p $PROJECT_ROOT/{config,src/{backend,frontend,bot,plugin},scripts/{sync,ingest,embed,backup},data/{raw/{local,nas,yandex,google},processed,embeddings},backups,logs,tests/{backend,bot,scripts},notebooks,docs}

# Создание пустых лог-файлов
echo "Создание лог-файлов..."
touch $PROJECT_ROOT/logs/{sync,ingest,embed,api}.log

# Создание README.md
echo "Создание README.md..."
cat > $PROJECT_ROOT/README.md << 'EOF'
# RAG-Проект: Персональная система индексации документов

## Описание
Система для индексации, поиска и AI-анализа личных документов (Word, PowerPoint, Excel, PDF) из различных источников хранения.

## Структура проекта
- `config/` - Конфигурации и переменные окружения
- `src/` - Исходный код приложения
- `scripts/` - Утилиты и автоматизация
- `data/` - Данные проекта
- `backups/` - Архивы и снимки
- `logs/` - Лог-файлы всех сервисов
- `tests/` - Тесты
- `notebooks/` - Jupyter-блокноты для анализа
- `docs/` - Документация проекта

## Настройка окружения
1. Скопируйте `.env.example` в `.env` и настройте переменные
2. Запустите `docker-compose up -d` для запуска сервисов
3. Настройте синхронизацию файлов через скрипты в `scripts/sync/`

## Запуск
Подробные инструкции по запуску находятся в документации: `/docs/user-guide.md`
EOF

# Создание .gitignore
echo "Создание .gitignore..."
cat > $PROJECT_ROOT/.gitignore << 'EOF'
# Игнорирование конфиденциальных данных
.env
*.pem
*.key
*.crt

# Игнорирование логов и временных файлов
logs/*.log
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
*.tmp

# Игнорирование каталогов данных
data/raw/*
data/processed/*
data/embeddings/*
backups/*

# Игнорирование каталогов зависимостей и сборки
node_modules/
__pycache__/
*.py[cod]
*$py.class
.pytest_cache/
dist/
build/
*.egg-info/

# Игнорирование IDE и редакторов
.idea/
.vscode/
*.swp
*.swo
.DS_Store
EOF

# Настройка прав доступа
echo "Настройка прав доступа..."
if [ "$(whoami)" = "root" ]; then
    chown -R raguser:raguser $PROJECT_ROOT
fi
chmod -R 750 $PROJECT_ROOT
chmod -R 700 $PROJECT_ROOT/config
chmod -R 700 $PROJECT_ROOT/data/raw
chmod -R 700 $PROJECT_ROOT/backups

echo "Структура каталогов успешно создана в $PROJECT_ROOT"
echo "Вы можете приступить к настройке конфигурационных файлов и разработке приложения."
