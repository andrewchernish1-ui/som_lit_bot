# Memory Bank - Литературный Помощник

## Архитектура проекта

**Бот работает в Docker-контейнере!** Не пытайся устанавливать зависимости в систему VPS - они нужны только внутри контейнера.

### Структура
- **Основной код**: Python + python-telegram-bot
- **ИИ**: OpenRouter API (DeepSeek)
- **База данных**: SQLite (простые словари)
- **Деплой**: Docker + docker-compose на VPS Ubuntu

### Файлы конфигурации
- `docker-compose.yml` - оркестрация контейнеров
- `Dockerfile` - сборка образа
- `requirements.txt` - Python зависимости
- `.env` - секретные ключи (токены)

## Восстановленная функциональность

### Кнопка меню (восстановлено 06.10.2025)
- **Проблема**: Пропала кнопка для вызова главного меню под ответами бота
- **Решение**: Добавлена кнопка "📋 Меню" под каждым ответом (объяснение слов, фраз, пересказ, характеристика)
- **Файлы изменены**:
  - `keyboards.py` - добавлена кнопка в get_response_actions_keyboard()
  - `handlers/callback_handler.py` - создан обработчик колбэк-запросов
  - `main.py` - подключен обработчик колбэк
  - Все handlers (word, phrase, retell, character) - добавлен reply_markup с кнопками

## Процесс обновления на VPS

**ПРАВИЛЬНЫЙ СПОСОБ** (через Docker):
```bash
cd ~/som_lit_bot
git pull origin main
docker-compose down
docker-compose up -d --build
docker-compose logs
```

**НЕПРАВИЛЬНЫЙ СПОСОБ** (не работает для Docker-приложений):
```bash
# НЕ ДЕЛАТЬ ЭТО!
pip3 install -r requirements.txt
python3 main.py &
```

## Ключевые команды VPS

### Обновление бота
```bash
cd ~/som_lit_bot
git pull origin main
docker-compose restart
```

### Проверка статуса
```bash
docker-compose ps
docker-compose logs -f
ps aux | grep python
```

### Резервное копирование
```bash
# Бэкап базы данных (если есть)
docker cp literary-bot:/app/database.db ./backup.db
```

### Логи и отладка
```bash
# Логи контейнера
docker-compose logs literary-bot

# Войти в контейнер
docker-compose exec literary-bot bash

# Проверить файлы
docker-compose exec literary-bot ls -la
```

## Известные проблемы и решения

1. **"ModuleNotFoundError: No module named 'telegram'"**
   - Причина: Попытка запуска вне Docker
   - Решение: Использовать docker-compose up --build

2. **Бот не отвечает в Telegram**
   - Проверить токен в .env
   - Проверить логи: `docker-compose logs`

3. **Кнопка меню не работает**
   - Проверить, что изменения в handlers/callback_handler.py
   - Проверить, что бот перезапущен

## Важные напоминания

- **Всегда используй Docker** для запуска/обновления
- **Не устанавливай зависимости в систему** - они только для контейнера
- **Проверяй логи** после каждого обновления
- **Делай git pull** перед обновлением Docker

## История изменений

- **06.10.2025**: Восстановлена кнопка меню под ответами бота
- **05.10.2025**: Убраны action-кнопки, вызвавшие пропажу меню
- **Ранее**: Добавлены функции анализа текста, характеристики героя

---

*Обновляй этот файл при внесении важных изменений в архитектуру или процессы.*
