"""Конфигурация бота"""
import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Telegram Bot
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
BOT_USERNAME = os.getenv('BOT_USERNAME')

# Google Gemini API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# Database
DATABASE_PATH = os.getenv('DATABASE_PATH', 'literary_bot.db')

# Admin
ADMIN_USER_ID = os.getenv('ADMIN_USER_ID')

# Validation
def validate_config():
    """Проверка наличия всех необходимых переменных окружения"""
    required_vars = [
        ('TELEGRAM_BOT_TOKEN', TELEGRAM_BOT_TOKEN),
        ('GOOGLE_API_KEY', GOOGLE_API_KEY),
    ]

    missing_vars = []
    for var_name, var_value in required_vars:
        if not var_value:
            missing_vars.append(var_name)

    if missing_vars:
        raise ValueError(f"Отсутствуют обязательные переменные окружения: {', '.join(missing_vars)}")

    return True

# Bot settings
MAX_MESSAGE_LENGTH = 4096  # Максимальная длина сообщения Telegram
QUIZ_OPTIONS_COUNT = 4     # Количество вариантов ответа в викторине
DEFAULT_LANGUAGE = 'ru'    # Язык по умолчанию
