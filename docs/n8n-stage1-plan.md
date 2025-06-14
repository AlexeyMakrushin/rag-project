# n8n RAG Автоматизация - Этап 1: Google Drive мониторинг и Word обработка

## Цель этапа
Создать автоматизированный pipeline в n8n для мониторинга Google Drive и обработки Word документов с сохранением в векторную базу Qdrant.

## Архитектура системы

### Структура данных
```
/Users/alexeymakrushin/Мой диск/makrushinrag/data/
├── original/              # Все файлы как есть (смешанная структура)
│   └── projects/rag/test/ # Пример существующей структуры  
├── processed/             # JSON файлы с зеркальной структурой
│   └── projects/rag/test/ # JSON версии документов
├── chunks/                # Не используется (чанки в JSON)
├── embeddings/            # Кеш эмбеддингов (опционально)
└── qdrant/               # База векторов
```

### Инфраструктура
- **n8n сервер**: n8n.mcrushin.ru (109.107.189.224)
- **Qdrant**: запущен в контейнере на том же сервере
- **Google Drive**: синхронизирован с локальной папкой
- **OpenAI API**: для генерации эмбеддингов

## n8n Workflow архитектура

### Узлы (Nodes) workflow:

1. **Google Drive Trigger**
   - Отслеживание папки: `makrushinrag/data/original`
   - События: создание, изменение файлов
   - Триггер: webhook от Google Drive API

2. **Switch Node - File Type Filter**
   - Ветка 1: Word документы (.docx, .doc) → обработка
   - Ветка 2: Excel (.xlsx, .xls) → заглушка (логирование)
   - Ветка 3: PowerPoint (.pptx, .ppt) → заглушка
   - Ветка 4: PDF → заглушка
   - Default: игнорировать

3. **Function Node - Word Text Extraction**
   - Библиотека: python-docx или mammoth
   - Извлечение: текст, заголовки, структура
   - Метаданные: путь, размер, дата изменения

4. **Function Node - Intelligent Chunking**
   - Размер чанка: 800-1200 токенов (~3000-4500 символов)
   - Семантические границы: заголовки, абзацы
   - Перекрытие: 100-200 токенов
   - Сохранение структуры документа

5. **Write File Node - Save Processed JSON**
   - Путь: `processed/` + зеркальная структура
   - Формат: JSON с чанками и метаданными
   - Создание папок автоматически

6. **OpenAI Node - Generate Embeddings**
   - Модель: text-embedding-ada-002
   - Батчинг: по 100 чанков
   - Обработка ошибок и лимитов

7. **HTTP Request - Upload to Qdrant**
   - Endpoint: `/collections/documents/points/upsert`
   - Формат: vectors + payload (метаданные)
   - ID чанков: uuid4

8. **Set Node - Logging & Results**
   - Логирование успешной обработки
   - Счетчики: файлов, чанков, эмбеддингов
   - Уведомления об ошибках

## Структура данных

### JSON файл обработанного документа:
```json
{
  "file_path": "original/projects/rag/test/document.docx",
  "processed_at": "2025-01-20T10:30:00Z",
  "metadata": {
    "filename": "document.docx",
    "size_bytes": 245760,
    "created_at": "2025-01-15T09:00:00Z",
    "modified_at": "2025-01-18T14:30:00Z",
    "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
  },
  "content": {
    "title": "Заголовок документа",
    "full_text": "Полный текст документа...",
    "structure": {
      "headings": ["Глава 1", "Глава 2"],
      "paragraphs_count": 25,
      "pages_estimated": 5
    }
  },
  "chunks": [
    {
      "chunk_id": "uuid-1",
      "sequence": 1,
      "text": "Первый чанк текста...",
      "token_count": 1024,
      "embedding_id": "qdrant-point-uuid-1",
      "metadata": {
        "heading": "Введение",
        "page_estimate": 1
      }
    },
    {
      "chunk_id": "uuid-2", 
      "sequence": 2,
      "text": "Второй чанк текста...",
      "token_count": 956,
      "embedding_id": "qdrant-point-uuid-2",
      "metadata": {
        "heading": "Глава 1",
        "page_estimate": 2
      }
    }
  ],
  "processing_stats": {
    "total_chunks": 12,
    "total_tokens": 11540,
    "processing_time_seconds": 45.2,
    "embedding_cost_usd": 0.012
  }
}
```

### Qdrant Point структура:
```json
{
  "id": "uuid-1",
  "vector": [0.1, 0.2, -0.1, ...],  // 1536 измерений
  "payload": {
    "file_path": "original/projects/rag/test/document.docx",
    "chunk_sequence": 1,
    "text": "Первый чанк текста...",
    "heading": "Введение",
    "document_title": "Заголовок документа",
    "file_type": "word",
    "processed_at": "2025-01-20T10:30:00Z",
    "token_count": 1024,
    "page_estimate": 1
  }
}
```

## Технические детали

### Интеллектуальный чанкинг для Word:
```python
def intelligent_chunk_word(doc_content, metadata):
    """
    Создает семантически осмысленные чанки из Word документа
    """
    chunks = []
    current_chunk = ""
    current_heading = ""
    token_count = 0
    
    for paragraph in doc_content.paragraphs:
        # Определяем заголовки по стилю
        if paragraph.style.name.startswith('Heading'):
            # Новый заголовок - завершаем текущий чанк
            if current_chunk and token_count > 500:
                chunks.append(create_chunk(current_chunk, current_heading))
                current_chunk = ""
                token_count = 0
            current_heading = paragraph.text
        
        # Добавляем абзац в чанк
        paragraph_text = paragraph.text
        paragraph_tokens = estimate_tokens(paragraph_text)
        
        # Если чанк становится слишком большим
        if token_count + paragraph_tokens > 1200:
            chunks.append(create_chunk(current_chunk, current_heading))
            current_chunk = paragraph_text
            token_count = paragraph_tokens
        else:
            current_chunk += "\n" + paragraph_text
            token_count += paragraph_tokens
    
    # Добавляем последний чанк
    if current_chunk:
        chunks.append(create_chunk(current_chunk, current_heading))
    
    return chunks
```

### Настройки Google Drive Trigger:
- **Watch For**: Files and Folders
- **Trigger On**: Created, Updated
- **Drive**: My Drive 
- **Folder**: `makrushinrag/data/original`
- **Polling Interval**: 1 minute

### Настройки OpenAI Node:
- **Operation**: Create Embeddings
- **Model**: text-embedding-ada-002  
- **Input**: {{ $json.text }}
- **Batch Size**: 100 (для экономии API calls)

### Настройки Qdrant HTTP Request:
- **Method**: POST
- **URL**: `http://localhost:6333/collections/documents/points/upsert`
- **Headers**: 
  - `Content-Type: application/json`
  - `api-key: your-qdrant-key` (если настроен)

## Обработка ошибок

### Возможные ошибки и решения:

1. **Google Drive API лимиты**
   - Retry с экспоненциальной задержкой
   - Кеширование результатов
   - Уведомления о превышении лимитов

2. **Ошибки извлечения текста**
   - Логирование проблемных файлов
   - Пропуск поврежденных документов
   - Альтернативные методы извлечения

3. **OpenAI API ошибки**
   - Rate limit handling
   - Fallback на другие модели
   - Кеширование эмбеддингов

4. **Qdrant недоступен**
   - Очередь для повторной отправки
   - Локальное сохранение векторов
   - Мониторинг состояния сервиса

## Мониторинг и логирование

### Метрики для отслеживания:
- Количество обработанных файлов в час
- Время обработки одного документа
- Стоимость OpenAI API calls
- Размер коллекции в Qdrant
- Ошибки и их частота

### Логи:
```json
{
  "timestamp": "2025-01-20T10:30:00Z",
  "workflow_id": "word-processing-pipeline",
  "file_path": "original/projects/doc.docx",
  "status": "success|error",
  "processing_time": 45.2,
  "chunks_created": 12,
  "tokens_processed": 11540,
  "embedding_cost": 0.012,
  "error_message": null
}
```

## Следующие этапы

### Этап 2: Обработка удаления и перемещения
- Отслеживание событий delete/move в Google Drive
- Удаление соответствующих векторов из Qdrant
- Обновление processed JSON файлов

### Этап 3: Расширение на другие типы файлов  
- Excel: обработка таблиц и формул
- PowerPoint: извлечение текста слайдов
- PDF: OCR и парсинг структуры

### Этап 4: Интерфейс поиска
- REST API для семантического поиска
- Веб-интерфейс для запросов
- Интеграция с существующими инструментами

## Готовые компоненты для реализации

1. **n8n Workflow JSON** - экспорт/импорт workflow
2. **Python функции** - для Function Node
3. **Qdrant схема коллекции** - создание индексов
4. **Тестовые данные** - для отладки pipeline

## Критерии успеха Этапа 1

✅ **Автоматическое обнаружение** новых Word файлов в Google Drive  
✅ **Извлечение текста** с сохранением структуры документа  
✅ **Интеллектуальное чанкинг** по семантическим границам  
✅ **Генерация эмбеддингов** через OpenAI API  
✅ **Сохранение в Qdrant** с полными метаданными  
✅ **JSON архив** обработанных документов  
✅ **Обработка ошибок** и логирование  
✅ **Масштабируемость** до 30-50GB документов
