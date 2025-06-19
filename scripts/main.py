# Файл: scripts/main.py
#
# Описание:
# Главный скрипт-оркестратор. Запускает все этапы процесса синхронизации
# в соответствии с утвержденным планом.

import os
from dotenv import load_dotenv

# Импортируем наши собственные модули
from get_gdrive_methadata import GDriveScanner
from db_client import SupabaseClient
import get_file_lists
import clone_files
import get_server_methadata # Импортируем новый сканер

def main():
    """Главная функция-оркестратор."""
    print("🚀 Запуск процесса полной сверки и синхронизации...")
    
    load_dotenv()
    GDRIVE_FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
    LOCAL_SYNC_PATH = os.getenv("LOCAL_SYNC_PATH") # Путь к /documents
    if not GDRIVE_FOLDER_ID or not LOCAL_SYNC_PATH:
        print("❌ Ошибка: Переменные GOOGLE_DRIVE_FOLDER_ID и LOCAL_SYNC_PATH должны быть заданы.")
        return

    # --- ЭТАП А: Синхронизация GDrive -> База -> Локальные Файлы ---
    print("\n" + "="*20 + " ЭТАП А: Синхронизация с Google Drive " + "="*20)
    
    # A.1. Сбор данных
    print("\n[A.1] Сбор данных с GDrive и из БД...")
    gdrive_scanner = GDriveScanner()
    if not gdrive_scanner.service: return
    
    gdrive_metadata = gdrive_scanner.get_metadata_from_gdrive(GDRIVE_FOLDER_ID)
    if gdrive_metadata is None: return
    print(f"  - Найдено {len(gdrive_metadata)} файлов на Google Drive.")

    db_client = SupabaseClient() # Клиент уже создан в модуле clone_files, но здесь он нужен для чтения
    db_mirror_data = db_client.get_all_documents()
    print(f"  - Получено {len(db_mirror_data)} записей из gdrive_mirror.")

    # A.2. Планирование (GDrive vs База)
    print("\n[A.2] Сравнение GDrive с базой данных...")
    to_create, to_update, to_move, to_delete = get_file_lists.get_gdrive_vs_db_plan(gdrive_metadata, db_mirror_data)
    print(f"  - План: Создать({len(to_create)}), Изменить({len(to_update)}), Переместить({len(to_move)}), Удалить({len(to_delete)})")

    # A.3. Исполнение плана
    print("\n[A.3] Выполнение плана синхронизации...")
    clone_files.execute_create(to_create)
    clone_files.execute_change(to_update)
    clone_files.execute_move(to_move)
    clone_files.execute_delete(to_delete)
    
    print("\n✅ ЭТАП А завершен.")


    # --- ЭТАП B: Контрольная проверка сервера ---
    print("\n" + "="*20 + " ЭТАП B: Контрольная проверка сервера " + "="*20)

    # B.1. Сбор данных
    print("\n[B.1] Сбор данных с сервера и из БД...")
    server_metadata = get_server_methadata.get_metadata_from_server(LOCAL_SYNC_PATH)
    db_mirror_data_updated = db_client.get_all_documents() # Перечитываем базу, она изменилась
    print(f"  - Получено {len(db_mirror_data_updated)} актуальных записей из gdrive_mirror.")
    
    # B.2. Планирование (Сервер vs База)
    print("\n[B.2] Сравнение сервера с базой данных...")
    to_refetch, to_delete_local = get_file_lists.get_server_vs_db_plan(server_metadata, db_mirror_data_updated)
    print(f"  - План проверки: Перекачать({len(to_refetch)}), Удалить локально({len(to_delete_local)})")
    
    # B.3. Исполнение плана "самоисцеления"
    # Для перезакачки мы можем переиспользовать нашу функцию execute_change,
    # т.к. она делает то же самое - качает файл и обновляет запись в БД.
    print("\n[B.3] Выполнение плана самоисцеления...")
    clone_files.execute_change(to_refetch)

    # Удаляем "мусорные" файлы с диска
    print(f"\n--- Удаление {len(to_delete_local)} 'мусорных' файлов с сервера ---")
    for relative_path in to_delete_local:
        full_path = os.path.join(LOCAL_SYNC_PATH, relative_path)
        print(f"-> Удаление: {full_path}")
        try:
            os.remove(full_path)
        except Exception as e:
            print(f"  ❌ Ошибка при удалении {full_path}: {e}")

    print("\n✅ ЭТАП B завершен.")
    
    print("\n✨✨✨ Процесс полной сверки и синхронизации завершен! ✨✨✨")


if __name__ == "__main__":
    main()