"""Обработчик пересказывания текста современным языком"""
from telegram import Update
from telegram.ext import ContextTypes
import logging
from llm_service import generate_text_retelling, initialize_llm_service
from keyboards import get_response_actions_keyboard

logger = logging.getLogger(__name__)

async def retell_text(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> None:
    """
    Пересказать текст современным языком

    Args:
        update: Объект обновления Telegram
        context: Контекст обработчика
        text (str): Исходный текст для пересказывания
    """
    user_id = update.effective_user.id

    try:
        logger.info(f"Пользователь {user_id} запросил пересказ текста (длина: {len(text)} символов)")

        # Проверяем длину исходного текста
        if len(text) > 5000:  # Ограничиваем для API
            logger.warning(f"Пользователь {user_id} отправил слишком длинный текст для пересказывания: {len(text)} символов")
            await update.message.reply_text(
                "❌ Текст слишком длинный (более 5000 символов).\n\n"
                "Пожалуйста, отправьте более короткий отрывок для пересказывания."
            )
            return

        # Отправляем сообщение о обработке (для больших текстов)
        if len(text) > 500:
            logger.info(f"Текст пользователя {user_id} длинный, показываем сообщение об обработке")
            processing_msg = await update.message.reply_text("🔄 Обрабатываю текст...")

        # Генерируем пересказ
        logger.info(f"Отправляем текст пользователя {user_id} в LLM API для пересказывания")

        # Инициализируем LLM сервис
        if not initialize_llm_service():
            logger.error("Не удалось инициализировать LLM сервис для пересказывания текста")
            await update.message.reply_text(
                "❌ Сервис временно недоступен. Попробуйте позже."
            )
            return

        retelling = generate_text_retelling(text)

        if retelling:
            response = f"📝 Современный пересказ:\n\n{retelling}"
            logger.info(f"LLM API успешно вернул пересказ для пользователя {user_id} (длина: {len(retelling)} символов)")

            # Проверяем длину ответа
            max_length = 4000
            if len(response) > max_length:
                logger.warning(f"Пересказ для пользователя {user_id} слишком длинный, обрезаем до {max_length} символов")
                response = response[:max_length-100] + "\n\n... [Пересказ обрезан из-за ограничений Telegram]"
        else:
            logger.error(f"LLM API не смог пересказать текст для пользователя {user_id}")
            response = (
                "❌ Не удалось пересказать текст.\n\n"
                "Возможно, текст слишком сложный или содержит неподдерживаемые символы. "
                "Попробуйте отправить более короткий и понятный отрывок."
            )

        # Удаляем сообщение о обработке, если оно было
        if len(text) > 500 and 'processing_msg' in locals():
            try:
                await processing_msg.delete()
                logger.info(f"Удалено сообщение об обработке для пользователя {user_id}")
            except Exception as e:
                logger.warning(f"Не удалось удалить сообщение об обработке для пользователя {user_id}: {e}")

        logger.info(f"Отправляем пересказ пользователю {user_id}")
        await update.message.reply_text(
            response,
            reply_markup=get_response_actions_keyboard()
        )

        logger.info(f"Успешно выполнен пересказ текста для пользователя {user_id}")

    except Exception as e:
        logger.error(f"Критическая ошибка при пересказывании текста для пользователя {user_id}: {e}", exc_info=True)
        await update.message.reply_text(
            "❌ Произошла ошибка при пересказывании текста. Попробуйте отправить другой текст."
        )
