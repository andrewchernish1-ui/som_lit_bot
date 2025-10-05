"""Клавиатуры и меню для бота"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup

def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Создает главное меню с кнопками основных функций"""
    keyboard = [
        ["1️⃣ Объяснить слово"],
        ["2️⃣ Разобрать фразу/абзац"],
        ["3️⃣ Пересказать современным языком"],
        ["4️⃣ Характеристика героя"]
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

def get_response_actions_keyboard(word: str = None) -> InlineKeyboardMarkup:
    """Создает клавиатуру действий для ответа бота"""
    keyboard = []

    if word:
        keyboard.append([
            InlineKeyboardButton("📚 Добавить в словарь", callback_data=f"add_word_{word}"),
            InlineKeyboardButton("⭐ Оценить ответ", callback_data="rate_response")
        ])

    keyboard.append([
        InlineKeyboardButton("🔄 Объяснить иначе", callback_data="explain_again"),
        InlineKeyboardButton("❓ Задать вопрос", callback_data="ask_question")
    ])

    return InlineKeyboardMarkup(keyboard)

def get_popular_terms_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру с популярными литературными терминами"""
    terms = [
        ["метафора", "метонимия"],
        ["ирония", "гипербола"],
        ["аналогия", "аллегория"],
        ["📖 Другие термины", "🎭 Пословицы"]
    ]

    keyboard = []
    for row in terms:
        keyboard_row = []
        for term in row:
            if "📖" in term or "🎭" in term:
                keyboard_row.append(InlineKeyboardButton(term, callback_data=f"category_{term.replace('📖 ', '').replace('🎭 ', '').lower()}"))
            else:
                keyboard_row.append(InlineKeyboardButton(term, callback_data=f"term_{term}"))
        keyboard.append(keyboard_row)

    return InlineKeyboardMarkup(keyboard)
