#!/bin/bash
# install_docker.sh - Скрипт для установки Docker и Docker Compose

# Проверка запуска от root
if [ "$(id -u)" != "0" ]; then
   echo "Этот скрипт должен быть запущен с правами root" 1>&2
   exit 1
fi

echo "Начинаем установку Docker и Docker Compose..."

# Установка зависимостей
echo "Установка зависимостей..."
apt update
apt install -y apt-transport-https ca-certificates curl software-properties-common gnupg

# Добавление официального GPG-ключа Docker
echo "Добавление GPG-ключа Docker..."
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Добавление репозитория Docker
echo "Добавление репозитория Docker..."
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# Установка Docker Engine
echo "Установка Docker Engine..."
apt update
apt install -y docker-ce docker-ce-cli containerd.io

# Установка Docker Compose
echo "Установка Docker Compose..."
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Добавление пользователя raguser в группу docker
echo "Настройка прав доступа..."
usermod -aG docker raguser

# Включение и запуск Docker
echo "Запуск и включение Docker..."
systemctl enable docker
systemctl start docker

# Создание docker сети для контейнеров
echo "Создание Docker сети..."
docker network create ragnet

# Проверка установки
echo "Проверка установки..."
docker --version
docker-compose --version
docker run hello-world

echo "Docker и Docker Compose успешно установлены!"
