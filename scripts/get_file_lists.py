# Файл: scripts/get_file_lists.py
#
# Описание:
# Этот модуль содержит логику для сравнения двух состояний:
# 1. Актуальное состояние в Google Drive.
# 2. Состояние последней синхронизации, сохраненное в базе данных (gdrive_mirror).
#
# На основе сравнения он формирует план действий, разделяя все файлы
# на 4 категории: на создание, на изменение, на перемещение и на удаление.

from typing import Dict, Any, List, Tuple
from datetime import datetime, timezone

# --- Функция 1: Сравнение GDrive с Базой ---
def get_gdrive_vs_db_plan(
    gdrive_data: Dict[str, Dict],
    db_data: Dict[str, Dict]
) -> Tuple[List, List, List, List]:
    # (Эта функция остается без изменений)
    gdrive_ids = set(gdrive_data.keys())
    db_ids = set(db_data.keys())

    delete_ids = db_ids - gdrive_ids
    to_delete = list(delete_ids)

    create_ids = gdrive_ids - db_ids
    to_create = [gdrive_data[id] for id in create_ids]

    common_ids = gdrive_ids.intersection(db_ids)
    to_update = []
    to_move = []

    for id in common_ids:
        gdrive_item = gdrive_data[id]
        db_item = db_data[id]

        if gdrive_item['md5_checksum'] != db_item.get('md5_checksum'):
            to_update.append(gdrive_item)
            continue

        if gdrive_item['path'] != db_item.get('path'):
            to_move.append(gdrive_item)

    return to_create, to_update, to_move, to_delete


# --- Функция 2: Контрольная проверка Сервера с Базой ---
def get_server_vs_db_plan(
    server_data: Dict[str, Dict],
    db_data: Dict[str, Dict]
) -> Tuple[List, List]:
    """
    Сравнивает файлы на сервере с записями в БД и находит несоответствия.

    Args:
        server_data: Словарь файлов с сервера, ключ - относительный путь.
        db_data: Словарь из БД, преобразованный так, что ключ - относительный путь.

    Returns:
        Кортеж из двух списков:
        - to_refetch (list): Метаданные файлов из БД, которые нужно перекачать.
        - to_delete_local (list): Относительные пути "мусорных" файлов для удаления с сервера.
    """
    server_paths = set(server_data.keys())
    
    # Преобразуем данные из БД для удобного поиска по пути
    db_paths_map = {item['path']: item for item in db_data.values()}
    db_paths = set(db_paths_map.keys())

    # 1. Найти "мусорные" файлы: есть на сервере, но нет в актуальной базе.
    delete_local_paths = server_paths - db_paths
    to_delete_local = list(delete_local_paths)
    
    # 2. Проверить общие файлы на несоответствие размера.
    # Это быстрая проверка вместо медленного хэширования.
    common_paths = server_paths.intersection(db_paths)
    to_refetch = []
    
    for path in common_paths:
        server_item = server_data[path]
        db_item = db_paths_map[path]
        
        # Сравниваем размеры. Если не совпадают - файл был изменен локально.
        if server_item['size_bytes'] != db_item['size_bytes']:
            # Добавляем в список на перезакачку всю информацию из БД
            to_refetch.append(db_item)
            
    # 3. Также нужно перезакачать файлы, которые есть в базе, но отсутствуют на диске.
    missing_on_server_paths = db_paths - server_paths
    for path in missing_on_server_paths:
        to_refetch.append(db_paths_map[path])

    return to_refetch, to_delete_local