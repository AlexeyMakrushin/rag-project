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
