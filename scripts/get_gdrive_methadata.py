# Файл: scripts/get_gdrive_methadata.py
#
# Описание:
# Этот модуль отвечает за взаимодействие с Google Drive API.
# Он содержит класс GDriveScanner, который выполняет аутентификацию
# и получает полный рекурсивный список метаданных для всех файлов
# в указанной папке на Google Drive.

import os
import json
from typing import Dict, Any, Optional

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from tqdm import tqdm

class GDriveScanner:
    """
    Класс для сканирования Google Drive, инкапсулирующий аутентификацию и получение данных.
    """
    SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
    CREDENTIALS_FILE = "credentials.json"
    TOKEN_FILE = "token.json"

    def __init__(self):
        """
        Инициализатор класса. При создании объекта сразу же выполняет
        аутентификацию и создает готовый к работе сервис-клиент.
        """
        self.creds = self._authenticate()
        if self.creds:
            self.service = build("drive", "v3", credentials=self.creds)
            print("✅ Аутентификация в Google Drive прошла успешно.")
        else:
            self.service = None
            print("❌ Не удалось аутентифицироваться в Google Drive.")

    def _authenticate(self) -> Optional[Credentials]:
        # (Этот приватный метод аутентификации остается без изменений, он надежен)
        creds = None
        if os.path.exists(self.TOKEN_FILE) and os.path.getsize(self.TOKEN_FILE) > 0:
            try:
                creds = Credentials.from_authorized_user_file(self.TOKEN_FILE, self.SCOPES)
            except json.JSONDecodeError:
                creds = None
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.CREDENTIALS_FILE, self.SCOPES)
                creds = flow.run_console()
            
            with open(self.TOKEN_FILE, "w") as token:
                token.write(creds.to_json())
        return creds

    def get_metadata_from_gdrive(self, folder_id: str) -> Optional[Dict[str, Dict[str, Any]]]:
        """
        Рекурсивно получает метаданные всех файлов из указанной папки.

        Args:
            folder_id (str): ID корневой папки для сканирования.

        Returns:
            Словарь, где ключ - это gdrive_id, а значение - словарь с метаданными файла.
            Возвращает None в случае ошибки.
        """
        if not self.service:
            print("Ошибка: сервис Google Drive не инициализирован.")
            return None

        all_files = {}
        folders_to_visit = [(folder_id, "")]
        
        print("Сканирование Google Drive...")
        try:
            with tqdm(total=len(folders_to_visit), desc="Анализ папок") as pbar:
                while folders_to_visit:
                    current_folder_id, current_path = folders_to_visit.pop(0)
                    
                    page_token = None
                    while True:
                        response = self.service.files().list(
                            q=f"'{current_folder_id}' in parents and trashed=false",
                            fields="nextPageToken, files(id, name, mimeType, md5Checksum, version, webViewLink, createdTime, modifiedTime, size)",
                            pageToken=page_token
                        ).execute()
                        
                        for file in response.get('files', []):
                            file_path = os.path.join(current_path, file.get("name"))
                            if file.get('mimeType') == 'application/vnd.google-apps.folder':
                                folders_to_visit.append((file['id'], file_path))
                                pbar.total += 1
                            else:
                                all_files[file.get("id")] = {
                                    "gdrive_id": file.get("id"),
                                    "name": file.get("name"),
                                    "path": file_path,
                                    "md5_checksum": file.get("md5Checksum"),
                                    "version": file.get("version"),
                                    "mime_type": file.get("mimeType"),
                                    "web_view_link": file.get("webViewLink"),
                                    "gdrive_created_time": file.get("createdTime"),
                                    "gdrive_modified_time": file.get("modifiedTime"),
                                    "size_bytes": int(file.get("size", 0))
                                }
                        
                        page_token = response.get('nextPageToken')
                        if not page_token:
                            break
                    pbar.update(1)
        except HttpError as error:
            print(f"Произошла ошибка при доступе к Google Drive API: {error}")
            return None
        
        return all_files