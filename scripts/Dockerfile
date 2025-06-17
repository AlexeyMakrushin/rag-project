# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем системные зависимости, включая curl и unzip, которые нужны для установки rclone
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем rclone
RUN curl https://rclone.org/install.sh | bash

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файл с зависимостями и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальные файлы скриптов
COPY . .

# Команда по умолчанию (необязательно, но полезно для отладки)
CMD ["python", "main.py"]