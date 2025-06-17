# indexer.py
# Этот скрипт предназначен для индексации документов из указанной директории в векторную базу данных Qdrant.
# Он выполняет следующие шаги:
# 1. Загружает переменные окружения (API ключи, настройки Qdrant, пути).
# 2. Сканирует указанную директорию на наличие новых файлов (избегая повторной обработки уже проиндексированных).
# 3. Загружает и парсит содержимое каждого файла (поддерживаются различные форматы, такие как PDF, DOCX, TXT).
# 4. Разбивает извлеченный текст на более мелкие части (чанки).
# 5. Генерирует векторные представления (эмбеддинги) для каждого чанка с помощью выбранной модели (например, OpenAI).
# 6. Сохраняет эти эмбеддинги, текст чанков и метаданные (например, имя файла-источника) в Qdrant.

# --- Импорт необходимых библиотек ---
import os  # Для работы с операционной системой (пути к файлам, переменные окружения)
import time # Для добавления временных меток или задержек (здесь не используется активно, но может пригодиться)
from dotenv import load_dotenv  # Для загрузки переменных окружения из файла .env

# Библиотеки LangChain для работы с документами, текстом и векторными базами
from langchain_community.document_loaders import UnstructuredFileLoader # Для загрузки и парсинга различных типов файлов
from langchain_text_splitters import RecursiveCharacterTextSplitter # Для разбиения текста на чанки
from langchain_openai import OpenAIEmbeddings # Для создания эмбеддингов с помощью OpenAI API
# Если вы захотите использовать другие модели эмбеддингов, импортируйте их:
# from langchain_google_genai import GoogleGenerativeAIEmbeddings
# from langchain_community.embeddings import HuggingFaceEmbeddings # и т.д.

from langchain_qdrant import Qdrant # Для взаимодействия с Qdrant из LangChain
from qdrant_client import QdrantClient # Прямой клиент Qdrant, если нужны более низкоуровневые операции (здесь не используется напрямую для загрузки)

# --- Загрузка переменных окружения ---
# Эта функция загружает переменные из файла .env, который должен находиться в той же директории,
# где запускается скрипт, или в одной из родительских директорий.
# n8n также может устанавливать переменные окружения для команды, которую он выполняет.
load_dotenv()

# Получаем значения переменных окружения. Если переменная не найдена, используется значение по умолчанию (если указано).
# Директория, из которой будут читаться файлы для индексации.
# Пример: SYNC_DIRECTORY="/home/makrushin/makrushinrag/"
SYNC_DIRECTORY = os.getenv("SYNC_DIRECTORY")
if not SYNC_DIRECTORY:
    print("Ошибка: Переменная окружения SYNC_DIRECTORY не установлена.")
    exit(1) # Выход из скрипта с кодом ошибки

# Настройки Qdrant
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost") # Хост, где запущен Qdrant (по умолчанию localhost)
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333)) # Порт gRPC Qdrant (по умолчанию 6333)
QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "my_documents") # Имя коллекции в Qdrant

# API ключ для OpenAI (необходим для OpenAIEmbeddings)
# LangChain обычно автоматически подхватывает OPENAI_API_KEY из окружения,
# но явное получение может быть полезно для отладки или если нужно передать его куда-то еще.
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("Предупреждение: Переменная окружения OPENAI_API_KEY не установлена. OpenAIEmbeddings может не работать.")
    # Можно добавить exit(1) если ключ обязателен, но LangChain может его найти и без явного os.getenv

# Путь к файлу, где будут храниться имена уже обработанных файлов,
# чтобы избежать их повторной индексации.
# Рекомендуется использовать абсолютный путь или путь относительно директории скрипта,
# чтобы он корректно работал независимо от того, откуда запускается скрипт.
# Здесь мы предполагаем, что лог-файл будет лежать рядом со скриптом.
# script_dir = os.path.dirname(os.path.abspath(__file__)) # Директория, где находится сам скрипт
# PROCESSED_FILES_LOG = os.path.join(script_dir, "processed_files.log")
# Или можно задать через переменную окружения:
PROCESSED_FILES_LOG = os.getenv("PROCESSED_FILES_LOG", "processed_files.log") # По умолчанию - в текущей директории запуска

# --- Настройка моделей и параметров ---

# 1. Модель для создания эмбеддингов
# Выберите модель, которую вы хотите использовать. Убедитесь, что у вас есть доступ к соответствующему API и установлен ключ.
# Важно: модель эмбеддингов, используемая здесь для индексации, должна быть той же самой,
# что будет использоваться для эмбеддинга пользовательских запросов при поиске (в RAG workflow).
print(f"Используется модель эмбеддингов OpenAI...")
try:
    # Модели OpenAI: "text-embedding-3-small", "text-embedding-3-large", "text-embedding-ada-002"
    # "text-embedding-3-small" обычно хороший баланс качества и цены.
    embeddings_model = OpenAIEmbeddings(model="text-embedding-3-small", openai_api_key=OPENAI_API_KEY)
except Exception as e:
    print(f"Ошибка инициализации OpenAI Embeddings: {e}")
    print("Убедитесь, что OPENAI_API_KEY установлен и действителен.")
    exit(1)

# Пример для Google Gemini Embeddings (если бы вы его использовали):
# GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
# if not GOOGLE_API_KEY:
#     print("Предупреждение: GOOGLE_API_KEY не установлен для Gemini.")
# embeddings_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GOOGLE_API_KEY)

# 2. Параметры для разбиения текста на чанки
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1000)) # Желаемый размер каждого чанка в символах
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 200)) # Количество символов, на которое чанки будут пересекаться

# Инициализация сплиттера текста
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    length_function=len, # Функция для подсчета длины текста (стандартная len подходит для символов)
    is_separator_regex=False, # Если разделители - это регулярные выражения
)

# --- Функции для работы с логом обработанных файлов ---

def get_processed_files(log_filepath):
    """Загружает список уже обработанных файлов из лог-файла."""
    if not os.path.exists(log_filepath):
        return set() # Если файл не существует, возвращаем пустое множество
    try:
        with open(log_filepath, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip()) # Читаем строки, убираем пробелы и пустые строки
    except Exception as e:
        print(f"Ошибка чтения лог-файла {log_filepath}: {e}")
        return set() # В случае ошибки возвращаем пустое множество, чтобы не блокировать процесс

def add_to_processed_files(filepath, log_filepath):
    """Добавляет путь к файлу в лог-файл обработанных файлов."""
    try:
        with open(log_filepath, "a", encoding="utf-8") as f:
            f.write(filepath + "\n") # Добавляем путь и перенос строки
    except Exception as e:
        print(f"Ошибка записи в лог-файл {log_filepath} для файла {filepath}: {e}")

# --- Основная логика индексации ---

def main():
    """Главная функция скрипта индексации."""
    print("--- Начало процесса индексации ---")
    print(f"Директория для сканирования: {SYNC_DIRECTORY}")
    print(f"Файл лога обработанных файлов: {PROCESSED_FILES_LOG}")
    print(f"Qdrant хост: {QDRANT_HOST}, порт: {QDRANT_PORT}, коллекция: {QDRANT_COLLECTION_NAME}")

    # Получаем список уже обработанных файлов
    processed_files = get_processed_files(PROCESSED_FILES_LOG)
    print(f"Найдено {len(processed_files)} уже обработанных файлов.")

    all_new_documents_to_index = [] # Список для хранения всех документов (частей файлов), которые нужно проиндексировать

    # Рекурсивно обходим все файлы и поддиректории в SYNC_DIRECTORY
    print(f"Сканирование файлов в {SYNC_DIRECTORY}...")
    file_count = 0
    new_files_processed_count = 0
    for root, _, files in os.walk(SYNC_DIRECTORY):
        for filename in files:
            file_count += 1
            filepath = os.path.join(root, filename)

            # Проверяем, был ли файл уже обработан
            if filepath in processed_files:
                # print(f"Файл {filepath} уже обработан, пропускаем.")
                continue # Переходим к следующему файлу

            print(f"\nНайден новый файл для обработки: {filepath}")

            # Загрузка и парсинг файла
            # UnstructuredFileLoader пытается автоматически определить тип файла и извлечь текст.
            # Для некоторых форматов могут потребоваться дополнительные зависимости (например, для .doc, .epub).
            # Убедитесь, что вы установили их: pip install "unstructured[docx,pdf,pptx,md]" и т.д.
            try:
                # Стратегия "fast" быстрее, но может быть менее точной для сложных файлов.
                # "hi_res" лучше для PDF с изображениями или сложной структурой, но медленнее и требует доп. зависимостей.
                # "auto" пытается выбрать лучшую стратегию.
                loader = UnstructuredFileLoader(filepath, strategy="fast") # Пробуем "fast" для скорости
                # Если "fast" не справляется, можно попробовать "auto" или "hi_res" (для hi_res нужна библиотека detectron2)
                # loader = UnstructuredFileLoader(filepath, strategy="auto")
                
                raw_documents = loader.load() # Загружаем документ. Это вернет список объектов Document LangChain.
                                            # Обычно для одного файла это список из одного элемента.
                
                if not raw_documents:
                    print(f"Предупреждение: Файл {filepath} не удалось загрузить или он пуст.")
                    add_to_processed_files(filepath, PROCESSED_FILES_LOG) # Помечаем как обработанный, чтобы не пытаться снова
                    continue

                # Добавляем метаданные к каждому загруженному документу (или его частям, если loader разбил)
                # Важно: UnstructuredFileLoader может вернуть несколько "документов" из одного файла,
                # если файл имеет сложную структуру (например, разные секции).
                # Обычно же он возвращает один Document с полным текстом файла.
                for doc in raw_documents:
                    doc.metadata["source"] = filepath # Добавляем имя файла как источник
                    doc.metadata["filename"] = filename # Имя файла без пути
                    doc.metadata["processed_at"] = time.strftime("%Y-%m-%d %H:%M:%S") # Время обработки

                all_new_documents_to_index.extend(raw_documents) # Добавляем загруженные документы в общий список
                new_files_processed_count +=1

            except Exception as e:
                print(f"Ошибка обработки файла {filepath}: {e}")
                # Можно добавить файл в "ошибочные" или просто пропустить, чтобы не блокировать весь процесс.
                # Здесь мы его не добавляем в processed_files.log, чтобы попытаться обработать в следующий раз.
                # Если ошибка повторяется, файл нужно будет исследовать вручную.

    print(f"\nСканирование завершено. Всего файлов найдено: {file_count}.")
    print(f"Новых файлов для обработки найдено (до чанкинга): {new_files_processed_count}.")

    if not all_new_documents_to_index:
        print("Нет новых документов для индексации.")
        print("--- Процесс индексации завершен (нет новых данных) ---")
        return # Выходим, если нет новых документов

    # 3. Разбиение документов на чанки
    print("\nРазбиение документов на чанки...")
    try:
        chunked_documents = text_splitter.split_documents(all_new_documents_to_index)
    except Exception as e:
        print(f"Ошибка при разбиении документов на чанки: {e}")
        # Если здесь ошибка, то все новые документы не будут проиндексированы.
        # Можно было бы попытаться разбить их по одному, чтобы изолировать проблему.
        exit(1) # Критическая ошибка, выходим

    if not chunked_documents:
        print("После чанкинга не осталось документов для индексации (возможно, все файлы были пустыми или слишком короткими).")
        # Помечаем все исходные файлы как обработанные, если они были загружены, но не дали чанков
        for doc_initial in all_new_documents_to_index:
            if "source" in doc_initial.metadata:
                 add_to_processed_files(doc_initial.metadata["source"], PROCESSED_FILES_LOG)
        print("--- Процесс индексации завершен (нет чанков для индексации) ---")
        return

    print(f"Документы разбиты на {len(chunked_documents)} чанков.")

    # 4. Индексация чанков в Qdrant
    print("\nИндексация чанков в Qdrant...")
    print(f"Коллекция: {QDRANT_COLLECTION_NAME}, Хост: {QDRANT_HOST}, Порт: {QDRANT_PORT}")

    try:
        # Qdrant.from_documents пытается создать коллекцию, если она не существует,
        # или добавить документы в существующую.
        # Важно: если коллекция создается впервые, она будет создана с конфигурацией по умолчанию
        # для векторов (размерность будет взята из первого эмбеддинга).
        # Если нужна специфическая конфигурация коллекции (например, on_disk=True),
        # ее лучше создать заранее через QdrantClient.
        
        # Пример создания коллекции с QdrantClient, если нужно больше контроля:
        # client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        # try:
        #     client.get_collection(collection_name=QDRANT_COLLECTION_NAME)
        #     print(f"Коллекция '{QDRANT_COLLECTION_NAME}' уже существует.")
        # except Exception: # Если коллекции нет, будет исключение
        #     print(f"Коллекция '{QDRANT_COLLECTION_NAME}' не найдена, создаем новую...")
        #     vector_size = embeddings_model.client.get_embedding_dim() # Получаем размерность эмбеддингов (зависит от клиента модели)
        #     client.recreate_collection(
        #         collection_name=QDRANT_COLLECTION_NAME,
        #         vectors_config=models.VectorParams(size=vector_size, distance=models.Distance.COSINE) # Пример конфигурации
        #     )
        
        Qdrant.from_documents(
            documents=chunked_documents, # Список чанков (объектов Document LangChain)
            embedding=embeddings_model,    # Модель для создания эмбеддингов
            host=QDRANT_HOST,
            port=QDRANT_PORT,
            collection_name=QDRANT_COLLECTION_NAME,
            prefer_grpc=True, # Обычно gRPC быстрее для больших объемов данных
            # force_recreate=False # Установить в True, если хотите каждый раз пересоздавать коллекцию (для тестов)
        )
        print(f"Успешно проиндексировано {len(chunked_documents)} чанков в коллекцию '{QDRANT_COLLECTION_NAME}'.")

        # После успешной индексации, помечаем исходные файлы как обработанные
        # Мы берем source из метаданных чанков. Так как один файл мог дать несколько чанков,
        # используем set, чтобы не дублировать записи в лог.
        indexed_source_files = set()
        for chunk in chunked_documents:
            if "source" in chunk.metadata:
                indexed_source_files.add(chunk.metadata["source"])
        
        for filepath in indexed_source_files:
            add_to_processed_files(filepath, PROCESSED_FILES_LOG)
        print(f"Файлы, из которых были взяты чанки, помечены как обработанные в {PROCESSED_FILES_LOG}.")

    except Exception as e:
        print(f"Критическая ошибка во время индексации в Qdrant: {e}")
        print("Данные из этой сессии не были полностью проиндексированы, и файлы не помечены как обработанные.")
        # В этом случае файлы не будут добавлены в processed_files.log,
        # и скрипт попытается обработать их снова при следующем запуске.
        exit(1) # Выход с ошибкой

    print("\n--- Процесс индексации успешно завершен ---")

# --- Точка входа в скрипт ---
if __name__ == "__main__":
    # Этот блок выполняется только тогда, когда скрипт запускается напрямую (а не импортируется как модуль)
    try:
        main()
    except Exception as e:
        print(f"Непредвиденная ошибка верхнего уровня: {e}")
        exit(1) # Выход с ошибкой, чтобы n8n мог это отследить