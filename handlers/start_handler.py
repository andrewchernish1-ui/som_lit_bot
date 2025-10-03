"""Обработчик команды /start"""
from telegram import Update
from telegram.ext import ContextTypes
from keyboards import get_main_menu_keyboard

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет приветственное сообщение и главное меню"""
    user = update.effective_user

    welcome_text = (
        f"👋 Привет, {user.mention_html()}!\n\n"
        "Я — Литературный Помощник 🤖\n"
        "Я помогу тебе читать сложные тексты, объясню редкие слова, "
        "разберу фразы и перескажу современным языком.\n\n"
        "Выбери функцию из меню ниже:"
    )

    await update.message.reply_html(
        welcome_text,
        reply_markup=get_main_menu_keyboard()
    )
