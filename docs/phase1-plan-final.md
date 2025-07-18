# План реализации Этапа 1: Базовая инфраструктура

## Цели этапа

- Создание базовой структуры проекта
- Реализация сканера директорий и файлов
- Проектирование и настройка детальной схемы SQLite
- Реализация экстракторов текста для различных форматов документов
- Создание базового CLI для управления процессами

## Детальные задачи и требования

### 1. Структура проекта

**Задача**: Разработать модульную структуру проекта, настроить окружение и систему управления зависимостями.

**Требования**:
- Модульная организация кода с четким разделением ответственностей
- Настройка системы логирования с различными уровнями
- Настройка системы тестирования (unit-тесты и интеграционные тесты)
- Конфигурация через YAML-файлы с возможностью переопределения через переменные окружения
- Система управления зависимостями (requirements.txt или Poetry)

**Структура каталогов**:
```
doc_vbz/
├── src/
│   ├── scanner/         # Модули для сканирования файлов
│   ├── extractors/      # Модули для извлечения текста
│   ├── storage/         # Модули для работы с базами данных
│   ├── models/          # Модели данных (SQLAlchemy)
│   ├── utils/           # Утилиты (логирование, конфигурация)
│   └── cli/             # CLI-интерфейс
├── scripts/             # Скрипты для запуска процессов
├── tests/               # Тесты
│   ├── unit/            # Модульные тесты
│   └── integration/     # Интеграционные тесты
├── data/                # Данные
│   ├── db/              # База данных SQLite
│   └── test_files/      # Тестовые файлы
├── config/              # Конфигурационные файлы
├── logs/                # Логи
└── docs/                # Документация
```

### 2. Детальное проектирование схемы базы данных

**Задача**: Разработать детальную схему базы данных SQLite с учетом будущей миграции на PostgreSQL.

**Требования**:
- Использование SQLAlchemy для абстракции доступа к БД
- Полное определение всех таблиц, колонок и связей
- Оптимизация схемы для основных запросов
- Создание индексов для ускорения поиска
- Подготовка миграций для будущих изменений схемы

**Детальная схема**:

```
# Таблица файлов
files:
  id: INTEGER PRIMARY KEY
  path: TEXT UNIQUE              # Полный путь к файлу
  filename: TEXT                 # Имя файла
  file_hash: TEXT                # SHA-256 хеш содержимого
  content_hash: TEXT             # Хеш извлеченного текста (для выявления "почти дубликатов")
  mime_type: TEXT                # MIME-тип файла
  size: INTEGER                  # Размер файла в байтах
  created_time: TIMESTAMP        # Дата создания
  modified_time: TIMESTAMP       # Дата изменения
  indexed_time: TIMESTAMP        # Дата индексации
  extraction_quality: TEXT       # Качество извлечения текста (good, partial, failed)
  status: TEXT                   # Статус обработки (indexed, failed, processing)
  indexing_error: TEXT           # Ошибка индексации (если есть)
  
# Таблица извлеченного контента
content:
  id: INTEGER PRIMARY KEY
  file_id: INTEGER FOREIGN KEY   # Ссылка на файл
  content_type: TEXT             # Тип контента (text, json, structure)
  content: TEXT                  # Извлеченный текст или JSON
  language: TEXT                 # Определенный язык контента
  metadata: TEXT                 # JSON с дополнительными метаданными
  extracted_at: TIMESTAMP        # Дата и время извлечения
  
# Таблица версий файлов
file_versions:
  id: INTEGER PRIMARY KEY
  original_id: INTEGER FOREIGN KEY  # Ссылка на оригинальный файл
  version_id: INTEGER FOREIGN KEY   # Ссылка на версию файла
  similarity: REAL                  # Степень сходства (0.0-1.0)
  version_type: TEXT                # Тип версии (exact_duplicate, near_duplicate, revision)
  created_time: TIMESTAMP           # Дата создания связи
  
# Таблица моделей эмбеддингов (для отслеживания версий)
embedding_models:
  id: INTEGER PRIMARY KEY
  name: TEXT                     # Название модели
  version: TEXT                  # Версия модели
  dimensions: INTEGER            # Размерность векторов
  description: TEXT              # Описание модели
  is_active: BOOLEAN             # Активна ли модель
  created_at: TIMESTAMP          # Дата добавления
```

### 3. Сканер файловой системы

**Задача**: Разработать модуль для сканирования директорий, определения типов файлов и их хеширования.

**Требования**:
- Рекурсивное обхождение директорий с возможностью фильтрации по типам файлов и размеру
- Вычисление SHA-256 хеша для каждого файла для идентификации изменений
- Извлечение базовых метаданных (размер, дата создания/изменения, MIME-тип)
- Обработка ошибок доступа к файлам и логирование проблем
- Поддержка как полного сканирования, так и инкрементального (только новые/измененные файлы)
- Опционально: поддержка периодического сканирования через cron или мониторинга через watchdog

**Основные функции**:
- `scan_directory()` - полное сканирование директории
- `incremental_scan()` - сканирование только новых или измененных файлов
- `calculate_file_hash()` - вычисление хеша файла
- `get_file_metadata()` - получение метаданных файла
- `filter_files()` - фильтрация файлов по различным критериям

### 4. Экстракторы текста

**Задача**: Разработать модули для извлечения текста и метаданных из различных форматов документов с оценкой качества извлечения.

**Требования**:
- Создание универсального интерфейса для различных типов экстракторов
- Реализация экстракторов для основных форматов:
  - PDF (с учетом сложных макетов и сканированных документов)
  - MS Office (DOCX, XLSX, PPTX)
  - Текстовые форматы (TXT, MD, CSV)
  - HTML и другие веб-форматы
- Извлечение не только текста, но и структуры документа (заголовки, параграфы, таблицы)
- Сохранение извлеченного текста как в виде чистого текста, так и в структурированном формате JSON
- Оценка качества извлечения с маркировкой проблемных документов
- Определение языка текста
- Извлечение встроенных метаданных (автор, дата, заголовок)

**Архитектура экстракторов**:
- Базовый абстрактный класс `BaseExtractor` с общим интерфейсом
- Специализированные классы для каждого формата
- Фабрика экстракторов для выбора подходящего экстрактора по MIME-типу
- Комбинированные экстракторы для сложных форматов (например, PDF + OCR)

**Используемые библиотеки**:
- `unstructured` - универсальный экстрактор для различных форматов
- `Docling` - альтернативный экстрактор с сохранением структуры
- `PyMuPDF` (fitz) - для работы с PDF, особенно с сложными макетами
- `python-docx`, `openpyxl`, `python-pptx` - для специфичных форматов при необходимости
- `langid` или `fasttext` - для определения языка

### 5. CLI-интерфейс

**Задача**: Разработать интерфейс командной строки для управления функциями системы.

**Требования**:
- Команды для сканирования директорий (`scan`)
- Команды для извлечения текста (`extract`)
- Команды для управления базой данных (`db`) с подкомандами:
  - `init` - инициализация БД
  - `stats` - статистика по БД
  - `clean` - очистка БД
- Команды для просмотра информации о файлах (`info`)
- Богатое форматирование вывода для улучшения читаемости
- Детальное логирование операций с возможностью настройки уровня детализации
- Интерактивный режим для некоторых команд

**Используемые библиотеки**:
- `Typer` - создание CLI-интерфейса
- `rich` - для форматированного вывода

## План реализации

### Неделя 1: Настройка проекта и базовый сканер (5-7 дней)

1. **День 1-2**: Настройка структуры проекта
   - Создание структуры каталогов
   - Настройка окружения и зависимостей
   - Создание базовых конфигурационных файлов
   - Настройка логирования

2. **День 3-5**: Разработка модуля сканирования
   - Реализация функций обхода директорий
   - Реализация функций хеширования файлов
   - Реализация функций получения метаданных файлов
   - Разработка фильтров для файлов

3. **День 6-7**: Тестирование сканера
   - Разработка тестов для сканера
   - Отладка и оптимизация
   - Документирование модуля

### Неделя 2: Проектирование базы данных и экстракторы (6-8 дней)

1. **День 1-3**: Детальное проектирование схемы SQLite
   - Определение всех таблиц и связей
   - Создание моделей SQLAlchemy
   - Реализация базовых операций CRUD
   - Разработка тестов для БД

2. **День 4-8**: Базовые экстракторы текста
   - Реализация интерфейса экстрактора
   - Интеграция unstructured для универсального извлечения
   - Реализация специфичных экстракторов для PDF и DOCX
   - Определение языка текста
   - Оценка качества извлечения

### Неделя 3: Интеграция и CLI (5-7 дней)

1. **День 1-3**: Интеграция компонентов
   - Объединение сканера, БД и экстракторов
   - Реализация конвейера обработки файлов
   - Разработка интеграционных тестов
   - Оптимизация конвейера

2. **День 4-7**: Разработка CLI
   - Создание базовых команд
   - Реализация форматированного вывода
   - Разработка интерактивного режима
   - Тестирование CLI на различных сценариях

### Неделя 4: Тестирование и оптимизация (5-7 дней)

1. **День 1-3**: Комплексное тестирование
   - Тестирование на различных типах файлов
   - Тестирование на больших объемах данных
   - Выявление и исправление ошибок
   - Оптимизация производительности

2. **День 4-7**: Финализация Этапа 1
   - Завершение документации
   - Рефакторинг кода
   - Подготовка к Этапу 2
   - Создание отчета о результатах Этапа 1

## Ожидаемые результаты

По завершении Этапа 1 мы получим:

1. Хорошо структурированный проект с модульной архитектурой
2. Функциональный сканер файловой системы с поддержкой инкрементальных обновлений
3. Детально спроектированную базу данных SQLite с моделями SQLAlchemy
4. Набор экстракторов текста для различных форматов с оценкой качества извлечения
5. CLI-интерфейс для управления основными функциями системы

Эти компоненты создадут прочную основу для дальнейшей работы над индексацией и анализом на следующих этапах.

## Метрики успеха

- **Сканирование**: обработка 1000+ файлов без сбоев, с корректным определением типов и хешированием
- **Извлечение текста**: успешное извлечение из >90% поддерживаемых форматов с пометкой проблемных случаев
- **Производительность**: сканирование и хеширование со скоростью >5 файлов/сек, извлечение текста >1 МБ/сек
- **Надежность**: корректная обработка ошибок, логирование и восстановление после сбоев
- **Тесты**: >80% покрытия кода тестами

## Потенциальные риски и их минимизация

- **Сложные форматы документов**: подготовить тестовый набор с проблемными случаями, использовать комбинацию экстракторов
- **Производительность на больших объемах**: применять пакетную обработку, оптимизировать запросы к БД
- **Ошибки доступа к файлам**: разработать надежную обработку ошибок и механизмы повторных попыток
- **Миграция на PostgreSQL**: с самого начала использовать SQLAlchemy и абстрагировать доступ к БД
