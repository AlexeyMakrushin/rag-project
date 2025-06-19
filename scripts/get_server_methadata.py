# Файл: scripts/get_server_methadata.py
#
# Описание:
# Этот модуль сканирует локальную директорию на сервере и собирает
# сокращенный набор метаданных о файлах для контрольной сверки.

import os
from typing import Dict, Any

def get_metadata_from_server(local_path: str) -> Dict[str, Dict[str, Any]]:
    """
    Рекурсивно сканирует локальную директорию и собирает метаданные.

    Args:
        local_path: Абсолютный путь к корневой директории для сканирования.

    Returns:
        Словарь, где ключ - это относительный путь файла, а значение -
        словарь с его метаданными (размер, время модификации).
    """
    server_files = {}
    print(f"Сканирование локальной директории: {local_path}...")
    for root, _, files in os.walk(local_path):
        for name in files:
            full_path = os.path.join(root, name)
            relative_path = os.path.relpath(full_path, local_path)
            
            try:
                stat = os.stat(full_path)
                server_files[relative_path] = {
                    'path': relative_path,
                    'size_bytes': stat.st_size,
                    'modified_time': stat.st_mtime # timestamp
                }
            except FileNotFoundError:
                # Файл мог быть удален во время сканирования, пропускаем
                continue
    print(f"✅ Найдено {len(server_files)} файлов на сервере.")
    return server_files