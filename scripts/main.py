# Файл: scripts/main.py
#
# Описание:
# Это главный исполняемый файл для процесса синхронизации.
# Он оркестрирует работу других модулей:
# 1. Получает учетные данные для доступа к Google Drive.
# 2. Получает список файлов с Google Drive.
# 3. (В будущем) Получает список файлов из локальной БД (Supabase).
# 4. (В будущем) Сравнивает списки и определяет, что нужно синхронизировать.
# 5. (В будущем) Выполняет синхронизацию (скачивание) и бэкап (загрузку).
#
# Для ручного запуска полной синхронизации выполните команду из корневой папки проекта:
# docker compose run --rm sync_service

import os
from dotenv import load_dotenv
from googleapiclient.discovery import build

# Импортируем наши собственные модули
import gdrive

def main():
    """Основная функция-оркестратор."""
    print("--- Запуск процесса полной сверки и синхронизации ---")
    
    # Загружаем переменные окружения из .env файла
    load_dotenv()
    google_drive_folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
    if not google_drive_folder_id:
        print("Ошибка: Переменная GOOGLE_DRIVE_FOLDER_ID не задана в .env файле.")
        return

    # 1. Аутентификация в Google
    print("\nШаг 1: Аутентификация в Google...")
    creds = gdrive.get_google_creds()
    if not creds:
        print("Не удалось пройти аутентификацию Google. Процесс прерван.")
        return
    
    # Создаем авторизованный клиент для работы с API
    drive_service = build("drive", "v3", credentials=creds)

    # 2. Получение списка файлов с Google Drive
    print("\nШаг 2: Получение списка удаленных файлов...")
    remote_files = gdrive.get_all_remote_files(drive_service, google_drive_folder_id)
    
    if remote_files:
        print(f"\nУспешно найдено {len(remote_files)} файлов на Google Drive.")
    else:
        print("\nНе найдено файлов на Google Drive или произошла ошибка.")

    # --- TODO: Следующие шаги ---
    # 3. Получить список локальных записей из Supabase
    # 4. Сравнить удаленные файлы и локальные записи
    # 5. Выполнить синхронизацию документов (GDrive -> Сервер)
    # 6. Выполнить бэкап папок (Сервер -> GDrive)
    # 7. Сформировать отчет и отправить в Telegram

    print("\n--- Процесс завершен ---")

if __name__ == "__main__":
    main()