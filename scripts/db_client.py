# Файл: scripts/db_client.py
#
# Описание:
# Этот модуль предоставляет единую точку доступа к базе данных Supabase.
# Он содержит класс SupabaseClient, который инкапсулирует подключение
# и базовые операции чтения.

import os
from typing import Dict, Any
from supabase import create_client, Client
from dotenv import load_dotenv

class SupabaseClient:
    """Класс для инкапсуляции логики взаимодействия с Supabase."""
    def __init__(self):
        load_dotenv()
        url: str = os.environ.get("SUPABASE_URL")
        key: str = os.environ.get("SUPABASE_KEY")
        if not url or not key:
            raise ValueError("SUPABASE_URL и SUPABASE_KEY должны быть установлены в .env файле.")
        self.client: Client = create_client(url, key)
        self.table_name = "gdrive_mirror"
        print(f"✅ Supabase клиент успешно инициализирован для таблицы '{self.table_name}'.")

    def get_all_documents(self) -> Dict[str, Dict[str, Any]]:
        """
        Получает все записи из таблицы 'gdrive_mirror' для сверки.
        Возвращает словарь, где ключ - 'gdrive_id'.
        """
        try:
            # Запрашиваем поля, нужные для всех типов сравнений
            response = self.client.table(self.table_name).select(
                "gdrive_id, path, md5_checksum, size_bytes"
            ).execute()
            
            if response.data:
                return {item['gdrive_id']: item for item in response.data}
            return {}
        except Exception as e:
            print(f"❌ Ошибка при получении данных из Supabase: {e}")
            return {}