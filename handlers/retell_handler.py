"""Обработчик пересказывания текста современным языком"""
from telegram import Update
from telegram.ext import ContextTypes
import logging
from gemini_service import generate_text_retelling

logger = logging.getLogger(__name__)

async def retell_text(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> None:
    """
    Пересказать текст современным языком

    Args:
        update: Объект обновления Telegram
        context: Контекст обработчика
        text (str): Исходный текст для пересказывания
    """
    try:
        # Проверяем длину исходного текста
        if len(text) > 2000:  # Ограничиваем для API
            await update.message.reply_text(
                "❌ Текст слишком длинный (более 2000 символов).\n\n"
                "Пожалуйста, отправьте более короткий отрывок для пересказывания."
            )
            return

        # Отправляем сообщение о обработке (для больших текстов)
        if len(text) > 500:
            processing_msg = await update.message.reply_text("🔄 Обрабатываю текст...")

        # Генерируем пересказ
        retelling = generate_text_retelling(text)

        if retelling:
            response = f"📝 Современный пересказ:\n\n{retelling}"

            # Проверяем длину ответа
            max_length = 4000
            if len(response) > max_length:
                response = response[:max_length-100] + "\n\n... [Пересказ обрезан из-за ограничений Telegram]"
        else:
            response = (
                "❌ Не удалось пересказать текст.\n\n"
                "Возможно, текст слишком сложный или содержит неподдерживаемые символы. "
                "Попробуйте отправить более короткий и понятный отрывок."
            )

        # Удаляем сообщение о обработке, если оно было
        if len(text) > 500 and 'processing_msg' in locals():
            try:
                await processing_msg.delete()
            except:
                pass  # Игнорируем ошибки удаления

        await update.message.reply_text(response)

    except Exception as e:
        logger.error(f"Ошибка при пересказывании текста: {e}")
        await update.message.reply_text(
            "❌ Произошла ошибка при пересказывании текста. Попробуйте отправить другой текст."
        )
