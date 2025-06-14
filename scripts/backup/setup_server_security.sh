#!/bin/bash
# setup_server_security.sh - Скрипт для настройки базовой безопасности сервера

# Проверка запуска от root
if [ "$(id -u)" != "0" ]; then
   echo "Этот скрипт должен быть запущен с правами root" 1>&2
   exit 1
fi

echo "Начинаем настройку безопасности сервера..."

# Обновление системы и установка базовых утилит безопасности
echo "Обновление системы и установка утилит безопасности..."
apt update && apt upgrade -y
apt install -y fail2ban ufw vim htop tmux git curl wget unattended-upgrades

# Настройка автоматических обновлений безопасности
echo "Настройка автоматических обновлений..."
dpkg-reconfigure -plow unattended-upgrades

# Настройка временной зоны (Europe/Moscow)
echo "Настройка временной зоны..."
timedatectl set-timezone Europe/Moscow

# Настройка синхронизации времени
echo "Настройка синхронизации времени..."
apt install -y ntp
systemctl enable ntp
systemctl start ntp

# Настройка fail2ban для защиты от брутфорс-атак
echo "Настройка fail2ban..."
cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sed -i 's/bantime  = 10m/bantime  = 1h/' /etc/fail2ban/jail.local
systemctl enable fail2ban
systemctl restart fail2ban

# Настройка брандмауэра UFW
echo "Настройка брандмауэра UFW..."
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow http
ufw allow https
echo "y" | ufw enable

# Отключение парольной аутентификации SSH
echo "Настройка SSH для работы только с ключами..."
sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
systemctl restart sshd

# Создание непривилегированного пользователя для работы
echo "Создание пользователя raguser..."
adduser --disabled-password --gecos "" raguser
usermod -aG sudo raguser
mkdir -p /home/raguser/.ssh
touch /home/raguser/.ssh/authorized_keys

# Копирование публичного ключа root в authorized_keys пользователя raguser
cat /root/.ssh/id_rsa.pub >> /home/raguser/.ssh/authorized_keys

# Настройка прав доступа для .ssh директории
chmod 700 /home/raguser/.ssh
chmod 600 /home/raguser/.ssh/authorized_keys
chown -R raguser:raguser /home/raguser/.ssh

echo "Базовая настройка безопасности сервера завершена!"
echo "Теперь вы можете подключиться к серверу как пользователь raguser с использованием SSH-ключа"