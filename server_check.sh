#!/bin/bash
echo "Проверка состояния сервера 95.215.8.138"

# Проверка Docker
echo "=== Проверка Docker ==="
docker --version
docker ps -a

# Проверка контейнеров бота
echo "=== Проверка контейнеров бота ==="
docker ps -a | grep literary

# Проверка логов
echo "=== Логи контейнера ==="
if docker ps -q -f name=literary-bot | grep -q .; then
    docker logs literary-bot --tail 50
else
    echo "Контейнер literary-bot не найден или не запущен"
fi

# Проверка файлов проекта
echo "=== Проверка файлов проекта ==="
ls -la /root/
ls -la /root/som_lit_bot/ 2>/dev/null || echo "Директория som_lit_bot не найдена"

# Проверка процессов
echo "=== Проверка процессов Python ==="
ps aux | grep python

echo "=== Диагностика завершена ==="
