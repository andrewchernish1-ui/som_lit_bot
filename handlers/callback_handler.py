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
    else:
        # Неизвестный колбэк - просто показать меню
        from keyboards import get_main_menu_keyboard
        await query.message.reply_text(
            "📋 Выберите функцию из меню ниже:",
            reply_markup=get_main_menu_keyboard()
        )
