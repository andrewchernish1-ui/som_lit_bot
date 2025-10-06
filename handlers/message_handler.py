"""Обработчик текстовых сообщений и главного меню"""
from telegram import Update
from telegram.ext import ContextTypes
import logging

logger = logging.getLogger(__name__)

# Состояния пользователей для отслеживания контекста
USER_STATES = {}

# Константы состояний
STATE_NONE = 0
STATE_WAITING_WORD = 1
STATE_WAITING_PHRASE = 2
STATE_WAITING_RETELL = 3
STATE_WAITING_CHARACTER = 4

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает текстовые сообщения пользователя"""
    user_id = update.effective_user.id
    text = update.message.text.strip()

    # Получаем текущее состояние пользователя
    current_state = USER_STATES.get(user_id, STATE_NONE)

    try:
        if current_state == STATE_NONE:
            await handle_menu_selection(update, context, text)
        elif current_state == STATE_WAITING_WORD:
            await handle_word_request(update, context, text)
        elif current_state == STATE_WAITING_PHRASE:
            await handle_phrase_request(update, context, text)
        elif current_state == STATE_WAITING_RETELL:
            await handle_retell_request(update, context, text)
        elif current_state == STATE_WAITING_CHARACTER:
            await handle_character_request(update, context, text)

    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения: {e}")
        await update.message.reply_text(
            "❌ Произошла ошибка. Попробуйте еще раз."
        )

async def handle_menu_selection(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> None:
    """Обрабатывает выбор пункта главного меню"""
    user_id = update.effective_user.id

    if text.startswith("1️⃣") or text == "/слово":
        USER_STATES[user_id] = STATE_WAITING_WORD
        await update.message.reply_text(
            "📝 Введите слово, которое нужно объяснить:"
        )

    elif text.startswith("2️⃣") or text == "/объясни":
        USER_STATES[user_id] = STATE_WAITING_PHRASE
        await update.message.reply_text(
            "📖 Отправьте мне фразу, культурное понятие или имя для объяснения:"
        )

    elif text.startswith("3️⃣") or text == "/перескажи":
        USER_STATES[user_id] = STATE_WAITING_RETELL
        await update.message.reply_text(
            "🔄 Отправьте текст для пересказывания современным языком:"
        )

    elif text.startswith("4️⃣") or text == "/характер":
        USER_STATES[user_id] = STATE_WAITING_CHARACTER
        await update.message.reply_text(
            "🎭 Введите имя и фамилию героя, а также произведение (например: Обломов, Гончаров \"Обломов\"):"
        )

    else:
        from keyboards import get_main_menu_keyboard
        await update.message.reply_text(
            "❓ Пожалуйста, выберите функцию из меню или используйте команды:\n"
            "/слово - объяснить слово\n"
            "/объясни - разобрать фразу\n"
            "/перескажи - пересказать текст\n"
            "/характер - характеристика героя",
            reply_markup=get_main_menu_keyboard()
        )

async def handle_word_request(update: Update, context: ContextTypes.DEFAULT_TYPE, word: str) -> None:
    """Обрабатывает запрос объяснения слова"""
    user_id = update.effective_user.id

    # Сбрасываем состояние
    USER_STATES[user_id] = STATE_NONE

    try:
        from handlers.word_handler import explain_word
        await explain_word(update, context, word.lower())
    except Exception as e:
        logger.error(f"Ошибка при объяснении слова '{word}': {e}")
        await update.message.reply_text(
            f"❌ Не удалось объяснить слово '{word}'. Попробуйте другое слово."
        )

async def handle_phrase_request(update: Update, context: ContextTypes.DEFAULT_TYPE, phrase: str) -> None:
    """Обрабатывает запрос объяснения фразы"""
    user_id = update.effective_user.id

    # Сбрасываем состояние
    USER_STATES[user_id] = STATE_NONE

    try:
        from handlers.phrase_handler import explain_phrase
        await explain_phrase(update, context, phrase)
    except Exception as e:
        logger.error(f"Ошибка при объяснении фразы '{phrase[:50]}...': {e}")
        await update.message.reply_text(
            "❌ Не удалось объяснить фразу. Попробуйте сформулировать иначе."
        )

async def handle_retell_request(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> None:
    """Обрабатывает запрос пересказывания текста"""
    user_id = update.effective_user.id

    # Сбрасываем состояние
    USER_STATES[user_id] = STATE_NONE

    try:
        from handlers.retell_handler import retell_text
        await retell_text(update, context, text)
    except Exception as e:
        logger.error(f"Ошибка при пересказывании текста: {e}")
        await update.message.reply_text(
            "❌ Не удалось пересказать текст. Попробуйте отправить другой текст."
        )

async def handle_character_request(update: Update, context: ContextTypes.DEFAULT_TYPE, character_info: str) -> None:
    """Обрабатывает запрос характеристики героя"""
    user_id = update.effective_user.id

    # Сбрасываем состояние
    USER_STATES[user_id] = STATE_NONE

    try:
        from handlers.character_handler import characterize_hero
        await characterize_hero(update, context, character_info)
    except Exception as e:
        logger.error(f"Ошибка при характеристике героя '{character_info[:50]}...': {e}")
        await update.message.reply_text(
            "❌ Не удалось дать характеристику героя. Попробуйте сформулировать иначе."
        )
