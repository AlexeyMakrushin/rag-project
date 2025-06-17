# Файл: scripts/gdrive.py
#
# Описание:
# Этот модуль отвечает за все взаимодействия с Google Drive API.
# Он инкапсулирует логику аутентификации пользователя (получение и обновление токенов)
# и предоставляет функции для получения информации о файлах и папках на Google Drive.

import os
import json
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from tqdm import tqdm

# --- Константы ---
# Определяет уровень доступа. 'drive.readonly' - только чтение, что безопаснее.
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
TOKEN_PATH = "token.json"
CREDENTIALS_PATH = "credentials.json"

# --- Функции ---

def get_google_creds():
    """
    Проводит аутентификацию пользователя через OAuth2 и возвращает объект с учетными данными.

    При первом запуске инициирует процесс авторизации через браузер.
    Сохраняет полученный токен в `token.json` для последующих запусков.
    Автоматически обновляет токен, если его срок действия истек.

    Returns:
        google.oauth2.credentials.Credentials: Объект с учетными данными или None, если аутентификация не удалась.
    """
    creds = None
    # Проверяем, существует ли файл токена и не пустой ли он.
    if os.path.exists(TOKEN_PATH) and os.path.getsize(TOKEN_PATH) > 0:
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
        except json.JSONDecodeError:
            print(f"Предупреждение: Файл {TOKEN_PATH} поврежден. Будет создан новый.")
            creds = None

    # Если учетные данные не найдены, или они недействительны, запускаем процесс получения новых.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Обновление просроченного токена...")
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Не удалось обновить токен: {e}. Запускаем полную аутентификацию.")
                creds = None # Сбрасываем, чтобы запустить полную аутентификацию
        
        # Если нужно, запускаем полную аутентификацию
        if not creds:
            print("Действительные учетные данные не найдены. Запуск процесса аутентификации...")
            try:
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
                creds = flow.run_console() 
            #    flow.redirect_uri = 'http://localhost:8080/'
            #    creds = flow.run_local_server(host='0.0.0.0', port=8080, open_browser=False)
            #    creds = flow.run_local_server(port=8080, open_browser=False)
            except Exception as e:
                print(f"Ошибка во время процесса аутентификации: {e}")
                return None

        # Сохраняем рабочие учетные данные в файл для будущих запусков.
        with open(TOKEN_PATH, "w") as token_file:
            token_file.write(creds.to_json())
        print(f"Учетные данные сохранены в {TOKEN_PATH}")
            
    return creds

def get_all_remote_files(service, folder_id: str) -> list:
    """
    Рекурсивно получает список всех файлов из указанной папки на Google Drive.

    Args:
        service: Авторизованный клиент Google Drive API.
        folder_id (str): ID корневой папки для сканирования.

    Returns:
        list: Список словарей, где каждый словарь представляет один файл и его метаданные.
              Возвращает пустой список в случае ошибки.
    """
    all_files = []
    # Стек для папок, которые нужно посетить: (id_папки, относительный_путь)
    folders_to_visit = [(folder_id, "")]

    print("Получение списка файлов с Google Drive...")
    try:
        with tqdm(total=1, desc="Сканирование папок") as pbar:
            while folders_to_visit:
                current_folder_id, current_path = folders_to_visit.pop(0)
                
                page_token = None
                while True:
                    response = service.files().list(
                        q=f"'{current_folder_id}' in parents and trashed = false",
                        spaces='drive',
                        fields='nextPageToken, files(id, name, mimeType, parents, modifiedTime, webViewLink, size, md5Checksum)',
                        pageToken=page_token
                    ).execute()
                    
                    for item in response.get('files', []):
                        item_path = os.path.join(current_path, item['name'])
                        if item['mimeType'] == 'application/vnd.google-apps.folder':
                            folders_to_visit.append((item['id'], item_path))
                            pbar.total += 1
                        else:
                            # Добавляем в метаданные наш собственный относительный путь
                            item['relative_path'] = item_path
                            all_files.append(item)
                    
                    page_token = response.get('nextPageToken', None)
                    if page_token is None:
                        break
                pbar.update(1)
    except HttpError as error:
        print(f"Произошла ошибка при доступе к Google Drive API: {error}")
        return []
    
    return all_files