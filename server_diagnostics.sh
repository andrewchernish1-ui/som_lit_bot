#!/bin/bash

echo "=== ДИАГНОСТИКА СОСТОЯНИЯ СЕРВЕРА ==="
echo "Время: $(date)"
echo "Сервер: $(hostname -I)"
echo ""

# Проверка Docker
echo "1. Проверка Docker:"
docker --version
echo "Статус Docker: $(systemctl is-active docker)"
echo ""

# Проверка контейнеров
echo "2. Проверка контейнеров:"
docker ps -a
echo ""

# Проверка логов бота
echo "3. Логи контейнера literary-bot:"
if docker ps -q -f name=literary-bot | grep -q .; then
    echo "Контейнер запущен, последние 20 строк логов:"
    docker logs literary-bot --tail 20
else
    echo "Контейнер literary-bot НЕ ЗАПУЩЕН!"
    echo "Проверка остановленных контейнеров:"
    docker ps -a | grep literary
fi
echo ""

# Проверка файлов проекта
echo "4. Проверка файлов проекта:"
echo "Содержимое /root:"
ls -la /root/
echo ""

echo "Содержимое директории проекта:"
if [ -d "/root/som_lit_bot" ]; then
    ls -la /root/som_lit_bot/
else
    echo "Директория /root/som_lit_bot НЕ НАЙДЕНА!"
fi
echo ""

# Проверка процессов Python
echo "5. Проверка процессов Python:"
ps aux | grep python
echo ""

# Проверка переменных окружения
echo "6. Проверка переменных окружения:"
if [ -f "/root/som_lit_bot/.env" ]; then
    echo "Файл .env найден:"
    ls -la /root/som_lit_bot/.env
    echo "Содержимое .env (без секретных данных):"
    grep -v "TOKEN\|KEY\|PASSWORD" /root/som_lit_bot/.env | head -10
else
    echo "Файл .env НЕ НАЙДЕН!"
fi
echo ""

# Проверка сети
echo "7. Проверка сети:"
echo "Порты в использовании:"
netstat -tlnp | grep -E ':(80|443|8080|3000|8000)'
echo ""

echo "=== ДИАГНОСТИКА ЗАВЕРШЕНА ==="
