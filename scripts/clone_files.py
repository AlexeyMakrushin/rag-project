# Файл: scripts/clone_files.py
# (Описание файла остается прежним)

import os
import subprocess
from typing import List, Dict
from db_client import SupabaseClient

# --- Константы из .env ---
# Теперь мы просто читаем переменные. Если их нет, main.py должен был прервать выполнение.
RCLONE_REMOTE_NAME = os.getenv("RCLONE_REMOTE_NAME")
LOCAL_SYNC_PATH = os.getenv("LOCAL_SYNC_PATH")

# --- Инициализация клиента БД ---
db_client = SupabaseClient()


def _clone_single_file_with_rclone(relative_path: str):
    """
    Клонирует один файл с GDrive на сервер, СОХРАНЯЯ СТРУКТУРУ ПАПОК.
    """
    if not RCLONE_REMOTE_NAME or not LOCAL_SYNC_PATH:
        print("  ❌ Ошибка: RCLONE_REMOTE_NAME или LOCAL_SYNC_PATH не заданы в .env")
        return False, "Переменные окружения не заданы"
        
    remote_source = f"{RCLONE_REMOTE_NAME}:" 
    local_destination = LOCAL_SYNC_PATH

    command = [
        "rclone", "copy",
        remote_source,
        local_destination,
        "--include", f"/{relative_path}", # Добавляем слэш в начало для точности
        "--create-empty-src-dirs",
        "--immutable",
        "--progress"
    ]
    
    print(f"  Выполнение: {' '.join(command)}")
    try:
        subprocess.run(command, check=True, capture_output=True, text=True, timeout=600)
        return True, None
    except subprocess.TimeoutExpired:
        error_message = "Таймаут скачивания файла (10 минут)."
        print(f"  ❌ {error_message}")
        return False, error_message
    except subprocess.CalledProcessError as e:
        # Убираем лишние переносы строк из вывода ошибки rclone
        error_details = e.stderr.strip().replace('\n', ' ')
        error_message = f"Rclone ошибка: {error_details}"
        print(f"  ❌ {error_message}")
        return False, error_message

#
# ОСТАЛЬНАЯ ЧАСТЬ ФАЙЛА (execute_create, execute_change, etc.) ОСТАЕТСЯ БЕЗ ИЗМЕНЕНИЙ
#
# ... (скопируйте сюда все функции execute_... из предыдущей версии) ...
#

def execute_create(files_to_create: List[Dict]):
    """Клонирует новые файлы с GDrive и создает записи в БД."""
    print(f"\n--- Обработка {len(files_to_create)} новых файлов ---")
    if not files_to_create:
        return

    successful_records = []
    for file_data in files_to_create:
        print(f"-> Создание файла: {file_data['path']}")
        is_success, error = _clone_single_file_with_rclone(file_data['path'])
        
        if is_success:
            file_data['status'] = 'SYNCED'
            successful_records.append(file_data)
        else:
            print(f"  ! Пропуск записи в БД для файла {file_data['path']} из-за ошибки скачивания.")
    
    if successful_records:
        print(f"\n-> Добавление {len(successful_records)} записей в gdrive_mirror...")
        db_client.client.table('gdrive_mirror').insert(successful_records).execute()
        print("  ✅ Записи успешно добавлены.")

def execute_change(files_to_change: List[Dict]):
    """Перезаписывает измененные файлы и обновляет их метаданные в БД."""
    print(f"\n--- Обработка {len(files_to_change)} измененных файлов ---")
    if not files_to_change:
        return

    for file_data in files_to_change:
        print(f"-> Обновление файла: {file_data['path']}")
        is_success, error = _clone_single_file_with_rclone(file_data['path'])
        
        if is_success:
            file_data['status'] = 'SYNCED'
            print(f"  -> Обновление записи в gdrive_mirror для ID {file_data['gdrive_id']}...")
            db_client.client.table('gdrive_mirror').update(file_data).eq('gdrive_id', file_data['gdrive_id']).execute()
            print("  ✅ Запись успешно обновлена.")
        else:
             print(f"  ! Пропуск обновления БД для файла {file_data['path']} из-за ошибки скачивания.")


def execute_move(files_to_move: List[Dict]):
    """Перемещает/переименовывает файлы локально и обновляет путь в БД."""
    print(f"\n--- Обработка {len(files_to_move)} перемещенных файлов ---")
    if not files_to_move:
        return

    for file_data in files_to_move:
        response = db_client.client.table('gdrive_mirror').select('path').eq('gdrive_id', file_data['gdrive_id']).single().execute()
        if not response.data: continue
        
        old_local_path = os.path.join(LOCAL_SYNC_PATH, response.data['path'])
        new_local_path = os.path.join(LOCAL_SYNC_PATH, file_data['path'])
        
        print(f"-> Перемещение: {old_local_path} -> {new_local_path}")
        try:
            if os.path.exists(old_local_path):
                os.makedirs(os.path.dirname(new_local_path), exist_ok=True)
                os.rename(old_local_path, new_local_path)
            else:
                print(f"  - Исходный файл {old_local_path} не найден, возможно, он не был скачан. Пропускаем перемещение.")
                continue

            print(f"  -> Обновление пути в gdrive_mirror для ID {file_data['gdrive_id']}...")
            db_client.client.table('gdrive_mirror').update({'path': file_data['path']}).eq('gdrive_id', file_data['gdrive_id']).execute()
            print("  ✅ Путь успешно обновлен.")
        except Exception as e:
            print(f"  ❌ Ошибка при перемещении файла {old_local_path}: {e}")

def execute_delete(ids_to_delete: List[str]):
    """Удаляет файлы локально и удаляет записи из БД."""
    print(f"\n--- Обработка {len(ids_to_delete)} удаленных файлов ---")
    if not ids_to_delete:
        return

    response = db_client.client.table('gdrive_mirror').select('gdrive_id, path').in_('gdrive_id', ids_to_delete).execute()
    files_to_remove_from_disk = response.data
    
    successfully_deleted_ids = []
    for file_info in files_to_remove_from_disk:
        local_path = os.path.join(LOCAL_SYNC_PATH, file_info['path'])
        print(f"-> Удаление файла: {local_path}")
        try:
            os.remove(local_path)
            successfully_deleted_ids.append(file_info['gdrive_id'])
        except FileNotFoundError:
            print("  - Файл уже отсутствует, считаем удаленным.")
            successfully_deleted_ids.append(file_info['gdrive_id'])
        except Exception as e:
            print(f"  ❌ Ошибка при удалении файла {local_path}: {e}")

    if successfully_deleted_ids:
        print(f"\n-> Удаление {len(successfully_deleted_ids)} записей из gdrive_mirror...")
        db_client.client.table('gdrive_mirror').delete().in_('gdrive_id', successfully_deleted_ids).execute()
        print("  ✅ Записи успешно удалены.")