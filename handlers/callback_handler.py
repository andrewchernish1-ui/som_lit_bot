"""Обработчик колбэк-запросов (inline кнопок)"""
from telegram import Update
from telegram.ext import ContextTypes
import logging
from keyboards import get_main_menu_keyboard

logger = logging.getLogger(__name__)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает колбэк-запросы от inline кнопок"""
    query = update.callback_query
    await query.answer()

    callback_data = query.data

    if callback_data == "show_menu":
        # Показать главное меню
        from keyboards import get_main_menu_keyboard
        await query.message.reply_text(
            "📋 Выберите функцию из меню ниже:",
            reply_markup=get_main_menu_keyboard()
        )
    elif callback_data.startswith("add_word_"):
        # Добавить слово в словарь (заглушка)
        word = callback_data.replace("add_word_", "")
        await query.message.reply_text(f"📚 Слово '{word}' добавлено в словарь!")
    elif callback_data == "rate_response":
        # Оценить ответ (заглушка)
        await query.message.reply_text("⭐ Спасибо за оценку!")
    elif callback_data == "explain_again":
        # Объяснить иначе (заглушка)
        await query.message.reply_text("🔄 Попробуем объяснить иначе...")
    elif callback_data == "ask_question":
        # Задать вопрос (заглушка)
        await query.message.reply_text("❓ Задайте свой вопрос:")
    else:
        # Неизвестный колбэк
        logger.warning(f"Неизвестный колбэк: {callback_data}")
