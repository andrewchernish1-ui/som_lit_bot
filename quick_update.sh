#!/bin/bash
echo "=== ОБНОВЛЕНИЕ СЕРВЕРА ==="
cd /root/som_lit_bot

echo "Получение изменений с GitHub..."
git pull origin main

echo "Остановка текущих контейнеров..."
docker-compose down

echo "Сборка и запуск новых контейнеров..."
docker-compose up -d --build

echo "Проверка статуса..."
docker ps -a | grep literary

echo "=== ОБНОВЛЕНИЕ ЗАВЕРШЕНО ==="
