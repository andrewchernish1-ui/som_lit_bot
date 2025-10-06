"""Главный файл Telegram-бота Литературный Помощник"""
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from config import TELEGRAM_BOT_TOKEN, validate_config

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def setup_handlers(application: Application) -> None:
    """Настройка обработчиков команд и сообщений"""

    # Обработчик команды /start
    from handlers.start_handler import start
    application.add_handler(CommandHandler("start", start))

    # Обработчик колбэк-запросов (Inline кнопки)
    from handlers.callback_handler import handle_callback
    application.add_handler(CallbackQueryHandler(handle_callback))

    # Обработчик всех остальных колбэк-запросов
    application.add_handler(CallbackQueryHandler(lambda u, c: u.callback_query.answer()))

    # Обработчик текстовых сообщений (главное меню, команды)
    from handlers.message_handler import handle_message
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

def main() -> None:
    """Главная функция запуска бота"""

    # Проверка конфигурации
    try:
        validate_config()
        logger.info("Конфигурация загружена успешно")
    except ValueError as e:
        logger.error(f"Ошибка конфигурации: {e}")
        return

    # Создание приложения
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Настройка обработчиков
    setup_handlers(application)

    # Запуск бота
    logger.info("Бот запущен и ожидает сообщений...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
