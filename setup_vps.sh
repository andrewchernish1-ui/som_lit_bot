#!/bin/bash

# Обновление системы
echo "Обновление системы..."
sudo apt update && sudo apt upgrade -y

# Установка Docker
echo "Установка Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo apt install -y docker-compose

# Клонирование репозитория
echo "Клонирование репозитория..."
git clone https://github.com/andrewchernish1-ui/som_lit_bot.git
cd som_lit_bot

# Создание директории для данных
echo "Создание директории для данных..."
mkdir -p data

# Запуск бота
echo "Запуск бота..."
sudo docker-compose up -d

echo "Настройка завершена. Бот запущен."
