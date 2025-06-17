# Файл: scripts/sync_and_meta.py

import os
import subprocess
import hashlib
from datetime import datetime, timezone

from dotenv import load_dotenv
from supabase import create_client, Client
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from tqdm import tqdm

# --- CONFIGURATION ---
# Загружаем переменные из .env файла.
# Docker Compose автоматически сделает их доступными как переменные окружения.
load_dotenv()

# Supabase Credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
# Google Drive Configuration
GOOGLE_DRIVE_FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
# Server Configuration
LOCAL_SYNC_PATH = os.getenv("LOCAL_SYNC_PATH") # Путь ВНУТРИ контейнера
RCLONE_REMOTE_NAME = os.getenv("RCLONE_REMOTE_NAME")

# Константы для путей к файлам аутентификации Google внутри контейнера
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
TOKEN_PATH = "token.json"  # Будет создан в /app/
CREDENTIALS_PATH = "credentials.json" # /app/credentials.json

# ... (остальные функции остаются без изменений, просто скопируйте их из предыдущего ответа) ...
# get_all_files_from_drive
# run_rclone_sync
# calculate_file_hash
# upsert_metadata_to_supabase
# main

# --- HELPER FUNCTIONS ---

def get_google_creds():
    """
    Аутентификация в Google API.
    При первом запуске потребует перейти по ссылке в браузере и вставить код авторизации в консоль.
    Создает token.json для последующих запусков.
    """
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Используем run_console() для окружений без графического интерфейса (Docker)
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_console()
        # Сохраняем учетные данные для следующего запуска
        with open(TOKEN_PATH, "w") as token:
            token.write(creds.to_json())
    return creds

def get_all_files_from_drive(service, folder_id: str) -> list:
    """Рекурсивно получает список всех файлов из указанной папки Google Drive."""
    all_files = []
    folders_to_visit = [(folder_id, "")]  # (folder_id, relative_path)

    print("Fetching file list from Google Drive...")
    pbar = tqdm(total=1)
    while folders_to_visit:
        current_folder_id, current_path = folders_to_visit.pop(0)
        pbar.set_description(f"Scanning folder: {current_path or '/'}")
        
        page_token = None
        while True:
            response = service.files().list(
                q=f"'{current_folder_id}' in parents and trashed = false",
                spaces='drive',
                fields='nextPageToken, files(id, name, mimeType, parents, modifiedTime, webViewLink, size)',
                pageToken=page_token
            ).execute()
            
            for item in response.get('files', []):
                item_path = os.path.join(current_path, item['name'])
                if item['mimeType'] == 'application/vnd.google-apps.folder':
                    folders_to_visit.append((item['id'], item_path))
                    pbar.total += 1
                else:
                    item['relative_path'] = item_path
                    all_files.append(item)
            
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break
        pbar.update(1)
    pbar.close()
    return all_files

def run_rclone_sync():
    """Запускает rclone для синхронизации файлов."""
    print("\nStarting file synchronization with rclone...")
    # rclone источник: "имя_remote:ID_папки_в_корне"
    # Это более надежный способ указать на конкретную папку
    rclone_source = f"{RCLONE_REMOTE_NAME}:{{{GOOGLE_DRIVE_FOLDER_ID}}}"
    command = [
        "rclone", "sync", rclone_source, LOCAL_SYNC_PATH,
        "--update",
        "--progress",
        "--transfers=8",
    ]
    try:
        subprocess.run(command, check=True)
        print("Rclone sync completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error during rclone sync: {e}")
        exit(1)
    except FileNotFoundError:
        print("Error: 'rclone' command not found. This should not happen in the Docker container.")
        exit(1)

def calculate_file_hash(file_path: str) -> str:
    """Вычисляет SHA256 хэш файла."""
    sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        return sha256.hexdigest()
    except FileNotFoundError:
        return None

def upsert_metadata_to_supabase(supabase: Client, files_metadata: list):
    """Обновляет/вставляет метаданные в Supabase."""
    print("\nUpserting metadata to Supabase...")
    records_to_upsert = []
    
    for meta in tqdm(files_metadata, desc="Preparing records"):
        # Путь к файлу внутри контейнера
        local_file_path = os.path.join(LOCAL_SYNC_PATH, meta['relative_path'])
        
        if not os.path.exists(local_file_path):
            print(f"Warning: File not found locally, skipping: {local_file_path}")
            continue

        file_hash = calculate_file_hash(local_file_path)
        
        record = {
            "gdrive_file_id": meta['id'],
            "file_name": meta['name'],
            "file_path": local_file_path, # Сохраняем путь внутри контейнера
            "file_type": os.path.splitext(meta['name'])[1],
            "file_size": int(meta.get('size', 0)),
            "created_at": meta['modifiedTime'],
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "source_folder": meta['parents'][0] if meta.get('parents') else None,
            "processing_status": 'synced',
            "mime_type": meta['mimeType'],
            "web_view_link": meta['webViewLink'],
            "file_hash": file_hash,
        }
        records_to_upsert.append(record)

    if records_to_upsert:
        try:
            supabase.table("documents").upsert(
                records_to_upsert, 
                on_conflict="gdrive_file_id"
            ).execute()
            print(f"\nSuccessfully upserted {len(records_to_upsert)} records to Supabase.")
        except Exception as e:
            print(f"An error occurred during Supabase upsert: {e}")

# --- MAIN EXECUTION ---
def main():
    """Основная функция-оркестратор."""
    print("--- Starting Google Drive Sync and Metadata Ingestion ---")
    
    creds = get_google_creds()
    drive_service = build("drive", "v3", credentials=creds)
    supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    drive_files = get_all_files_from_drive(drive_service, GOOGLE_DRIVE_FOLDER_ID)
    print(f"Found {len(drive_files)} files in Google Drive.")
    
    run_rclone_sync()
    
    upsert_metadata_to_supabase(supabase_client, drive_files)
    
    print("\n--- Process finished ---")

if __name__ == "__main__":
    main()