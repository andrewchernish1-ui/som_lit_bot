#!/bin/bash
echo "=== ДИАГНОСТИКА СЕРВЕРА ==="
echo "Время: $(date)"
echo ""

echo "1. Проверка контейнеров:"
docker ps -a
echo ""

echo "2. Логи контейнера literary-bot:"
if docker ps -q -f name=literary-bot | grep -q .; then
    echo "Контейнер запущен, последние 30 строк логов:"
    docker logs literary-bot --tail 30
else
    echo "Контейнер literary-bot НЕ ЗАПУЩЕН!"
    echo "Проверка остановленных контейнеров:"
    docker ps -a | grep literary
fi
echo ""

echo "3. Проверка файлов проекта:"
ls -la /root/som_lit_bot/
echo ""

echo "4. Проверка .env файла:"
if [ -f "/root/som_lit_bot/.env" ]; then
    echo "Файл .env найден:"
    grep -v "TOKEN\|KEY" /root/som_lit_bot/.env | head -5
else
    echo "Файл .env НЕ НАЙДЕН!"
fi
echo ""

echo "=== ДИАГНОСТИКА ЗАВЕРШЕНА ==="
