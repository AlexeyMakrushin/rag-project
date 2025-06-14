#!/bin/bash
# create_config_files.sh - Скрипт для создания базовых конфигурационных файлов

# Проверка запуска от пользователя raguser
if [ "$(whoami)" != "raguser" ] && [ "$(whoami)" != "root" ]; then
   echo "Этот скрипт должен быть запущен от пользователя raguser или root" 1>&2
   exit 1
fi

echo "Начинаем создание конфигурационных файлов..."

# Определение корневого каталога проекта
PROJECT_ROOT="/home/raguser/rag-project"

# Создание директории для конфигурационных файлов (если еще не создана)
mkdir -p $PROJECT_ROOT/config

# Создание шаблона .env файла
echo "Создание .env.example файла..."
cat > $PROJECT_ROOT/config/.env.example << 'EOF'
# Переменные окружения для RAG проекта
# Скопируйте этот файл в .env и заполните необходимыми значениями

# Общие настройки
ENVIRONMENT=development  # development, production
PROJECT_ROOT=/home/raguser/rag-project

# Настройки OpenAI API (для embeddings)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_EMBEDDING_MODEL=text-embedding-ada-002

# Настройки Anthropic API (для Claude)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Настройки Qdrant (векторная БД)
QDRANT_HOST=qdrant
QDRANT_PORT=6333
QDRANT_COLLECTION=documents

# Настройки синхронизации
SYNC_INTERVAL=3600  # в секундах
YANDEX_DISK_TOKEN=your_yandex_disk_token_here
GOOGLE_DRIVE_CREDENTIALS=your_google_drive_credentials_path_here

# Настройки API и веб-интерфейса
API_PORT=8000
WEB_PORT=3000
API_TOKEN=your_api_token_here

# Настройки Telegram бота
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_ADMIN_ID=your_telegram_user_id_here

# Настройки бэкапа
BACKUP_INTERVAL=86400  # в секундах (1 день)
BACKUP_RETENTION=7  # количество сохраняемых бэкапов
EOF

# Создание settings.yml файла
echo "Создание settings.yml файла..."
cat > $PROJECT_ROOT/config/settings.yml << 'EOF'
# Основные настройки проекта

# Настройки окружения
environment:
  name: development  # development, production
  debug: true

# Настройки файловой системы
file_system:
  max_file_size_mb: 50
  supported_formats:
    - pdf
    - docx
    - xlsx
    - pptx

# Настройки обработки документов
processing:
  chunk_size: 1000  # количество символов в чанке
  chunk_overlap: 200
  languages:
    - en
    - ru

# Настройки индексации
indexing:
  batch_size: 10  # количество файлов в пакете для обработки
  incremental: true  # инкрементальная индексация
  schedule: "0 2 * * *"  # ежедневно в 2:00 (cron формат)

# Настройки векторной БД
vector_db:
  collection_name: documents
  vector_size: 1536  # для OpenAI embedding модели
  distance: cosine  # cosine, euclid, dot
  
# Настройки AI моделей
ai_models:
  embedding:
    provider: openai
    model: text-embedding-ada-002
  generation:
    provider: anthropic
    model: claude-3-haiku-20240307
  
# Настройки API
api:
  rate_limit: 100  # запросов в минуту
  token_expiry: 86400  # в секундах (1 день)
  
# Настройки синхронизации
sync:
  enabled: true
  providers:
    - name: local
      enabled: true
    - name: nas
      enabled: true
      path: /mnt/nas
    - name: yandex
      enabled: true
    - name: google
      enabled: true
EOF

# Создание docker-compose.yml
echo "Создание docker-compose.yml..."
cat > $PROJECT_ROOT/docker-compose.yml << 'EOF'
version: '3.9'

services:
  # Векторная база данных Qdrant
  qdrant:
    image: qdrant/qdrant:latest
    container_name: rag-qdrant
    restart: unless-stopped
    volumes:
      - ./data/embeddings:/qdrant/storage
    ports:
      - "6333:6333"
      - "6334:6334"
    networks:
      - ragnet
    environment:
      - QDRANT_ALLOW_RECOVERY_MODE=true

  # API сервис (будет разработан позже)
  # api:
  #   build: ./src/backend
  #   container_name: rag-api
  #   restart: unless-stopped
  #   volumes:
  #     - ./data:/app/data
  #     - ./logs:/app/logs
  #   ports:
  #     - "8000:8000"
  #   networks:
  #     - ragnet
  #   env_file:
  #     - ./config/.env
  #   depends_on:
  #     - qdrant

  # Веб-интерфейс (будет разработан позже)
  # frontend:
  #   build: ./src/frontend
  #   container_name: rag-frontend
  #   restart: unless-stopped
  #   ports:
  #     - "3000:3000"
  #   networks:
  #     - ragnet
  #   env_file:
  #     - ./config/.env
  #   depends_on:
  #     - api

  # Telegram бот (будет разработан позже)
  # bot:
  #   build: ./src/bot
  #   container_name: rag-bot
  #   restart: unless-stopped
  #   volumes:
  #     - ./logs:/app/logs
  #   networks:
  #     - ragnet
  #   env_file:
  #     - ./config/.env
  #   depends_on:
  #     - api

networks:
  ragnet:
    name: ragnet
    external: true
EOF

# Документация к конфигурационным файлам
echo "Создание документации для конфигурационных файлов..."
cat > $PROJECT_ROOT/docs/config-guide.md << 'EOF'
# Руководство по конфигурации

Этот документ описывает все конфигурационные параметры системы и их назначение.

## Файл .env

Файл `.env` содержит переменные окружения, используемые различными компонентами системы.

### Общие настройки

- `ENVIRONMENT` - окружение (development, production)
- `PROJECT_ROOT` - корневой каталог проекта

### Настройки OpenAI API

- `OPENAI_API_KEY` - ключ API для доступа к OpenAI
- `OPENAI_EMBEDDING_MODEL` - модель для создания эмбеддингов (векторных представлений текста)

### Настройки Anthropic API

- `ANTHROPIC_API_KEY` - ключ API для доступа к моделям Anthropic Claude

### Настройки Qdrant

- `QDRANT_HOST` - хост для подключения к Qdrant
- `QDRANT_PORT` - порт для подключения к Qdrant
- `QDRANT_COLLECTION` - имя коллекции в Qdrant

### Настройки синхронизации

- `SYNC_INTERVAL` - интервал синхронизации в секундах
- `YANDEX_DISK_TOKEN` - токен для доступа к Yandex Disk
- `GOOGLE_DRIVE_CREDENTIALS` - путь к файлу учетных данных Google Drive

### Настройки API и веб-интерфейса

- `API_PORT` - порт для API сервиса
- `WEB_PORT` - порт для веб-интерфейса
- `API_TOKEN` - токен для доступа к API

### Настройки Telegram бота

- `TELEGRAM_BOT_TOKEN` - токен для Telegram бота
- `TELEGRAM_ADMIN_ID` - ID администратора в Telegram

### Настройки бэкапа

- `BACKUP_INTERVAL` - интервал создания бэкапов в секундах
- `BACKUP_RETENTION` - количество сохраняемых бэкапов

## Файл settings.yml

Файл `settings.yml` содержит конфигурацию компонентов системы.

### Настройки окружения

- `environment.name` - имя окружения (development, production)
- `environment.debug` - режим отладки (true/false)

### Настройки файловой системы

- `file_system.max_file_size_mb` - максимальный размер файла в МБ
- `file_system.supported_formats` - поддерживаемые форматы файлов

### Настройки обработки документов

- `processing.chunk_size` - размер чанка в символах
- `processing.chunk_overlap` - перекрытие чанков в символах
- `processing.languages` - поддерживаемые языки

### Настройки индексации

- `indexing.batch_size` - количество файлов в пакете для обработки
- `indexing.incremental` - инкрементальная индексация (true/false)
- `indexing.schedule` - расписание индексации (cron формат)

### Настройки векторной БД

- `vector_db.collection_name` - имя коллекции
- `vector_db.vector_size` - размер вектора
- `vector_db.distance` - метрика расстояния (cosine, euclid, dot)

### Настройки AI моделей

- `ai_models.embedding.provider` - провайдер для эмбеддингов
- `ai_models.embedding.model` - модель для эмбеддингов
- `ai_models.generation.provider` - провайдер для генерации текста
- `ai_models.generation.model` - модель для генерации текста

### Настройки API

- `api.rate_limit` - ограничение количества запросов в минуту
- `api.token_expiry` - время жизни токена в секундах

### Настройки синхронизации

- `sync.enabled` - включение синхронизации (true/false)
- `sync.providers` - провайдеры для синхронизации с настройками
EOF

# Настройка прав доступа
echo "Настройка прав доступа..."
if [ "$(whoami)" = "root" ]; then
    chown -R raguser:raguser $PROJECT_ROOT/config
    chown -R raguser:raguser $PROJECT_ROOT/docker-compose.yml
    chown -R raguser:raguser $PROJECT_ROOT/docs
fi
chmod 600 $PROJECT_ROOT/config/.env.example
chmod 600 $PROJECT_ROOT/config/settings.yml
chmod 644 $PROJECT_ROOT/docker-compose.yml
chmod 644 $PROJECT_ROOT/docs/config-guide.md

echo "Конфигурационные файлы успешно созданы!"
echo "Для настройки скопируйте .env.example в .env и отредактируйте значения:"
echo "cp $PROJECT_ROOT/config/.env.example $PROJECT_ROOT/config/.env"
