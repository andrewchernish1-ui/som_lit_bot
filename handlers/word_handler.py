"""Обработчик объяснения слов"""
from telegram import Update
from telegram.ext import ContextTypes
import logging
from literary_data import get_word_definition, format_word_response
from openrouter_service import generate_word_explanation
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
        logger.info(f"Пользователь {user_id} запросил объяснение слова: '{word}'")

        # Сначала пытаемся использовать OpenRouter API (приоритет)
        logger.info(f"Пытаемся получить объяснение слова '{word}' через OpenRouter API")
        explanation = generate_word_explanation(word)

        if explanation:
            # API успешно вернул объяснение
            logger.info(f"OpenRouter API успешно вернул объяснение слова '{word}' (длина: {len(explanation)} символов)")
            response = f"🤖 ИИ-генерация:\n\n{explanation}"
        else:
            # API не сработал, пробуем предварительную базу как fallback
            logger.warning(f"OpenRouter API не смог объяснить слово '{word}', пробуем предварительную базу")
            word_data = get_word_definition(word)

            if word_data:
                logger.info(f"Слово '{word}' найдено в предварительной базе данных")
                response = format_word_response(word_data)
                explanation = word_data['definition']
            else:
                # Ни API, ни база не сработали
                logger.error(f"Не удалось объяснить слово '{word}' ни через API, ни через базу данных")
                response = (
                    f"❌ К сожалению, я не смог объяснить слово '{word}'.\n\n"
                    "Возможно, это опечатка или очень редкое слово. "
                    "Попробуйте ввести другое слово или используйте команду /объясни для фраз."
                )
                await update.message.reply_text(response)
                return

        # Отправляем ответ пользователю
        logger.info(f"Отправляем ответ пользователю {user_id} для слова '{word}'")
        await update.message.reply_text(response)

        # Сохраняем слово в личный словарь пользователя (если объяснение удалось)
        if explanation:
            logger.info(f"Сохраняем слово '{word}' в личный словарь пользователя {user_id}")
            save_word(user_id, word, explanation)

        logger.info(f"Успешно обработан запрос на объяснение слова '{word}' для пользователя {user_id}")

    except Exception as e:
        logger.error(f"Критическая ошибка при объяснении слова '{word}' для пользователя {user_id}: {e}", exc_info=True)
        await update.message.reply_text(
            f"❌ Произошла ошибка при объяснении слова '{word}'. Попробуйте позже."
        )
