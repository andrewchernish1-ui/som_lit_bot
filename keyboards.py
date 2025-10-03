"""Клавиатуры и меню для бота"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup

def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Создает главное меню с кнопками основных функций"""
    keyboard = [
        ["1️⃣ Объяснить слово"],
        ["2️⃣ Разобрать фразу/абзац"],
        ["3️⃣ Пересказать современным языком"],
        ["4️⃣ Мой словарик"],
        ["🎲 Викторина"]
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False
    )

def get_quiz_keyboard(question: str, options: list, correct_index: int) -> InlineKeyboardMarkup:
    """Создает клавиатуру для викторины с вариантами ответов"""
    keyboard = []

    for i, option in enumerate(options):
        callback_data = f"quiz_{i}_{correct_index}"
        keyboard.append([InlineKeyboardButton(option, callback_data=callback_data)])

    return InlineKeyboardMarkup(keyboard)

def get_dictionary_actions_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру действий со словарем"""
    keyboard = [
        [InlineKeyboardButton("📄 Экспорт в PDF", callback_data="dict_export_pdf")],
        [InlineKeyboardButton("📊 Экспорт в таблицу", callback_data="dict_export_csv")],
        [InlineKeyboardButton("🗑️ Очистить словарь", callback_data="dict_clear")]
    ]

    return InlineKeyboardMarkup(keyboard)
