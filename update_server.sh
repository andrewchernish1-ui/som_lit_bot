#!/bin/bash
echo "Подключение к серверу и обновление бота..."

# Подключение к серверу и обновление проекта
ssh root@95.215.8.138 << 'ENDSSH'
echo "=== Обновление проекта на сервере ==="
cd /root/som_lit_bot

echo "Получение последних изменений из GitHub..."
git pull origin main

echo "Перезапуск контейнеров Docker..."
docker-compose down
docker-compose up -d --build

echo "Проверка статуса контейнеров..."
docker ps -a | grep literary

echo "=== Обновление завершено ==="
ENDSSH

echo "Скрипт создан. Теперь выполните: chmod +x update_server.sh && ./update_server.sh"
