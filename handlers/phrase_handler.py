"""Обработчик объяснения фраз и цитат"""
from telegram import Update
from telegram.ext import ContextTypes
import logging
from literary_data import get_phrase_explanation
from llm_service import generate_phrase_explanation, initialize_llm_service

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
            # Фраза не найдена, используем LLM API
            logger.info(f"Пытаемся объяснить фразу через LLM API: '{phrase[:50]}...'")

            # Отправляем сообщение "бот думает"
            processing_msg = await update.message.reply_text("🔄 Обрабатываю текст...")

            # Инициализируем LLM сервис
            if not initialize_llm_service():
                logger.error("Не удалось инициализировать LLM сервис для объяснения фразы")
                await update.message.reply_text(
                    "❌ Сервис временно недоступен. Попробуйте позже."
                )
                return

            explanation = generate_phrase_explanation(phrase)

            if explanation:
                logger.info(f"LLM API успешно объяснил фразу (длина: {len(explanation)} символов)")
                response = f"📝 Объяснение фразы:\n\n{explanation}"
            else:
                logger.warning(f"LLM API не смог объяснить фразу: '{phrase[:50]}...'")
                response = (
                    "❌ К сожалению, я не смог объяснить эту фразу.\n\n"
                    "Возможно, это слишком сложная цитата или у меня нет достаточного контекста. "
                    "Попробуйте упростить запрос или использовать /слово для отдельных терминов."
                )

        # Удаляем сообщение "бот думает" если оно было отправлено
        if 'processing_msg' in locals():
            try:
                await processing_msg.delete()
            except Exception as e:
                logger.warning(f"Не удалось удалить сообщение 'бот думает': {e}")

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
    response = f"🎭 {phrase_data['explanation']}"

    if phrase_data.get('modern_paraphrase'):
        response += f"\n\nСовременный вариант\n{phrase_data['modern_paraphrase']}"

    if phrase_data.get('cultural_context'):
        response += f"\n\nКультурный контекст\n{phrase_data['cultural_context']}"

    return response
