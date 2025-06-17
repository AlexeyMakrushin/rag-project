# Файл: generate_token.py
from google_auth_oauthlib.flow import InstalledAppFlow

# Определяем только самые необходимые константы
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
CREDENTIALS_PATH = "credentials.json"
TOKEN_PATH = "token.json"

print("--- Запуск локального генератора токенов ---")

try:
    # Запускаем самый надежный и простой метод авторизации
    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
    creds = flow.run_console()

    # Сохраняем полученные учетные данные в файл token.json
    with open(TOKEN_PATH, "w") as token_file:
        token_file.write(creds.to_json())
    
    print("\n--- УСПЕХ! ---")
    print(f"Файл {TOKEN_PATH} был успешно создан в этой папке.")
    print("Теперь скопируйте этот файл на ваш сервер в папку scripts.")

except Exception as e:
    print(f"\n--- ОШИБКА ---")
    print(f"Произошла ошибка: {e}")