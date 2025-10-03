"""Обработчик объяснения слов"""
from telegram import Update
from telegram.ext import ContextTypes
import logging
from literary_data import get_word_definition, format_word_response
from gemini_service import generate_word_explanation
from database import save_word

logger = logging.getLogger(__name__)

async def explain_word(update: Update, context: ContextTypes.DEFAULT_TYPE, word: str) -> None:
    """
    Объяснить слово пользователю

    Args:
        update: Объект обновления Telegram
        context: Контекст обработчика
        word (str): Слово для объяснения
    """
    user_id = update.effective_user.id

    try:
        # Сначала пытаемся найти в предварительной базе
        word_data = get_word_definition(word)

        if word_data:
            # Слово найдено в предварительной базе
            response = format_word_response(word_data)
            explanation = word_data['definition']
        else:
            # Слово не найдено, используем Gemini API
            explanation = generate_word_explanation(word)

            if explanation:
                response = f"🤖 ИИ-генерация:\n\n{explanation}"
            else:
                response = (
                    f"❌ К сожалению, я не смог объяснить слово '{word}'.\n\n"
                    "Возможно, это опечатка или очень редкое слово. "
                    "Попробуйте ввести другое слово или используйте команду /объясни для фраз."
                )
                await update.message.reply_text(response)
                return

        # Отправляем ответ пользователю
        await update.message.reply_text(response)

        # Сохраняем слово в личный словарь пользователя (если объяснение удалось)
        if explanation:
            save_word(user_id, word, explanation)

    except Exception as e:
        logger.error(f"Ошибка при объяснении слова '{word}': {e}")
        await update.message.reply_text(
            f"❌ Произошла ошибка при объяснении слова '{word}'. Попробуйте позже."
        )
