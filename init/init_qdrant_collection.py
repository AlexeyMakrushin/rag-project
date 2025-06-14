#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт для инициализации коллекции в Qdrant
Создает коллекцию с оптимальными параметрами для хранения векторов документов
Используется OpenAI text-embedding-3-small с размерностью 1536
"""

import os
import sys
import argparse
import logging
from datetime import datetime
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.exceptions import UnexpectedResponse

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/makrushin/rag-project/logs/qdrant_init.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('qdrant_init')

def parse_args():
    """Парсер аргументов командной строки"""
    parser = argparse.ArgumentParser(description='Инициализация коллекции Qdrant')
    parser.add_argument('--host', type=str, default='localhost', 
                        help='Qdrant host (default: localhost)')
    parser.add_argument('--port', type=int, default=6333, 
                        help='Qdrant port (default: 6333)')
    parser.add_argument('--collection', type=str, default='documents', 
                        help='Название коллекции (default: documents)')
    parser.add_argument('--api-key', type=str, default=None, 
                        help='API-ключ для Qdrant (берется из переменной окружения QDRANT_API_KEY, если не указан)')
    parser.add_argument('--recreate', action='store_true', 
                        help='Пересоздать коллекцию, если она уже существует')
    return parser.parse_args()

def init_collection(client, collection_name, recreate=False):
    """
    Инициализация коллекции в Qdrant с оптимальными параметрами
    
    Args:
        client: QdrantClient instance
        collection_name: Название коллекции
        recreate: Пересоздать коллекцию, если она существует
    
    Returns:
        bool: True, если коллекция успешно создана или уже существует
    """
    try:
        # Проверяем, существует ли коллекция
        collections = client.get_collections().collections
        collection_exists = any(collection.name == collection_name for collection in collections)
        
        if collection_exists:
            if recreate:
                logger.info(f"Коллекция {collection_name} уже существует, удаляем...")
                client.delete_collection(collection_name=collection_name)
            else:
                logger.info(f"Коллекция {collection_name} уже существует, пропускаем инициализацию")
                return True
        
        # Создаем коллекцию с оптимальными параметрами
        logger.info(f"Создаем коллекцию {collection_name}...")
        
        # Создаем схему для векторов из OpenAI text-embedding-3-small (1536D)
        # Используем Cosine для метрики расстояния
        # Включаем Scalar Quantization для экономии RAM
        # Настраиваем HNSW параметры: m=16, ef_construct=100, ef_search=64
        client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=1536,  # Размерность OpenAI text-embedding-3-small
                distance=models.Distance.COSINE,
                on_disk=True,  # Хранение векторов на диске для экономии RAM
                # Scalar Quantization для сжатия векторов
                quantization_config=models.ScalarQuantization(
                    scalar=models.ScalarQuantizationConfig(
                        type=models.ScalarType.INT8,
                        quantile=0.99,
                        always_ram=False
                    )
                )
            ),
            hnsw_config=models.HnswConfigDiff(
                m=16,               # Число исходящих связей в графе
                ef_construct=100,   # Размер динамического списка для построения индекса
                # ef_runtime удален, так как не поддерживается
                full_scan_threshold=10000,  # Порог для полного сканирования
                max_indexing_threads=4,     # Ограничиваем потоки индексации
                on_disk=True,       # Хранение индекса на диске
            ),
            optimizers_config=models.OptimizersConfigDiff(
                indexing_threshold=50000,     # Увеличиваем порог индексации
                memmap_threshold=50000,       # Порог для использования mmap
                vacuum_min_vector_number=1000  # Минимальное число векторов для очистки
            ),
            on_disk_payload=True  # Храним метаданные на диске для экономии RAM
        )
        
        # Создаем индексы для метаданных для ускорения фильтрации
        logger.info("Создаем индексы для метаданных...")
        client.create_payload_index(
            collection_name=collection_name,
            field_name="file_path",
            field_schema=models.PayloadSchemaType.KEYWORD
        )
        
        client.create_payload_index(
            collection_name=collection_name,
            field_name="source",
            field_schema=models.PayloadSchemaType.KEYWORD
        )
        
        client.create_payload_index(
            collection_name=collection_name,
            field_name="file_type",
            field_schema=models.PayloadSchemaType.KEYWORD
        )
        
        client.create_payload_index(
            collection_name=collection_name,
            field_name="last_modified",
            field_schema=models.PayloadSchemaType.DATETIME
        )
        
        logger.info(f"Коллекция {collection_name} успешно создана с оптимальными настройками")
        return True
        
    except UnexpectedResponse as e:
        logger.error(f"Ошибка при создании коллекции: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {str(e)}")
        return False

def main():
    """Основная функция скрипта"""
    args = parse_args()
    
    # Получаем API-ключ из аргументов или переменной окружения
    api_key = args.api_key or os.environ.get('QDRANT_API_KEY')
    if not api_key:
        logger.warning("API-ключ не указан. Используется подключение без аутентификации.")
    
    try:
        # Подключаемся к Qdrant
        client = QdrantClient(
            host=args.host,
            port=args.port,
            api_key=api_key,
            timeout=60,
            prefer_grpc=False,  # Используем REST API вместо gRPC
            https=False  # Используем HTTP вместо HTTPS
        )
        
        # Проверяем подключение
        logger.info("Проверка подключения к Qdrant...")
        client.get_collections()
        logger.info("Подключение к Qdrant успешно установлено")
        
        # Инициализируем коллекцию
        result = init_collection(client, args.collection, args.recreate)
        
        if result:
            logger.info("Инициализация коллекции успешно завершена")
            sys.exit(0)
        else:
            logger.error("Ошибка при инициализации коллекции")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Ошибка при подключении к Qdrant: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()