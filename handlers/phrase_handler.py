"""Обработчик объяснения фраз и цитат"""
from telegram import Update
from telegram.ext import ContextTypes
import logging
from literary_data import get_phrase_explanation
from openrouter_service import generate_phrase_explanation

logger = logging.getLogger(__name__)

async def explain_phrase(update: Update, context: ContextTypes.DEFAULT_TYPE, phrase: str) -> None:
    """
    Объяснить фразу или цитату пользователю

    Args:
        update: Объект обновления Telegram
        context: Контекст обработчика
        phrase (str): Фраза для объяснения
    """
    try:
        # Сначала пытаемся найти в предварительной базе
        phrase_data = get_phrase_explanation(phrase)

        if phrase_data:
            # Фраза найдена в предварительной базе
            response = format_phrase_response(phrase_data)
        else:
            # Фраза не найдена, используем Gemini API
            explanation = generate_phrase_explanation(phrase)

            if explanation:
                response = f"🤖 ИИ-генерация:\n\n{explanation}"
            else:
                response = (
                    f"❌ К сожалению, я не смог объяснить эту фразу.\n\n"
                    f"Фраза: '{phrase}'\n\n"
                    "Возможно, это слишком сложная цитата или у меня нет достаточного контекста. "
                    "Попробуйте упростить запрос или использовать /слово для отдельных терминов."
                )

        # Проверяем длину ответа - Telegram ограничивает 4096 символами
        max_length = 4000  # Даем запас

        if len(response) > max_length:
            # Если ответ слишком длинный, обрезаем и добавляем предупреждение
            response = response[:max_length-100] + "\n\n... [Ответ обрезан из-за ограничений Telegram]"

        await update.message.reply_text(response)

    except Exception as e:
        logger.error(f"Ошибка при объяснении фразы '{phrase[:50]}...': {e}")
        await update.message.reply_text(
            "❌ Произошла ошибка при объяснении фразы. Попробуйте сформулировать иначе."
        )

def format_phrase_response(phrase_data: dict) -> str:
    """
    Форматировать ответ для фразы

    Args:
        phrase_data (dict): Данные о фразе

    Returns:
        str: Отформатированный текст ответа
    """
    response = f"📖 {phrase_data['explanation']}"

    if phrase_data.get('modern_paraphrase'):
        response += f"\n\n🔍 Современный вариант: {phrase_data['modern_paraphrase']}"

    if phrase_data.get('cultural_context'):
        response += f"\n\n🌍 Культурный контекст: {phrase_data['cultural_context']}"

    return response
