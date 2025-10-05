"""Обработчик характеристики героя"""
from telegram import Update
from telegram.ext import ContextTypes
import logging
from llm_service import generate_character_description, initialize_llm_service

logger = logging.getLogger(__name__)

async def characterize_hero(update: Update, context: ContextTypes.DEFAULT_TYPE, character_info: str) -> None:
    """
    Даёт характеристику героя по имени, фамилии и произведению

    Args:
        update: Объект обновления Telegram
        context: Контекст обработчика
        character_info (str): Информация о герое (имя, фамилия, произведение)
    """
    user_id = update.effective_user.id

    try:
        logger.info(f"Пользователь {user_id} запросил характеристику героя: '{character_info}'")

        # Инициализируем LLM сервис при необходимости
        if not initialize_llm_service():
            logger.error("Не удалось инициализировать LLM сервис для характеристики героя")
            await update.message.reply_text(
                "❌ Сервис временно недоступен. Попробуйте позже."
            )
            return

        # Отправляем сообщение "бот думает"
        processing_msg = await update.message.reply_text("🔄 Обрабатываю текст...")

        # Генерируем характеристику героя
        logger.info(f"Отправляем информацию о герое '{character_info}' в LLM API для характеристики")

        description = generate_character_description(character_info)

        if description:
            response = f"🎭 Характеристика героя:\n\n{character_info}\n\n{description}"
            logger.info(f"LLM API успешно вернул характеристику для пользователя {user_id} (длина: {len(description)} символов)")
        else:
            logger.error(f"LLM API не смог дать характеристику героя для пользователя {user_id}")
            response = (
                f"❌ Не удалось дать характеристику героя '{character_info}'.\n\n"
                "Возможно, информация о герое недостаточна или такого героя нет в известных произведениях. "
                "Попробуйте указать имя, фамилию и произведение более точно."
            )

        # Удаляем сообщение о обработке
        try:
            await processing_msg.delete()
        except Exception as e:
            logger.warning(f"Не удалось удалить сообщение об обработке для пользователя {user_id}: {e}")

        # Проверяем длину ответа
        max_length = 4000
        if len(response) > max_length:
            logger.warning(f"Характеристика героя для пользователя {user_id} слишком длинная, обрезаем до {max_length} символов")
            response = response[:max_length-100] + "\n\n... [Характеристика обрезана из-за ограничений Telegram]"

        logger.info(f"Отправляем характеристику героя пользователю {user_id}")
        await update.message.reply_text(response)

        logger.info(f"Успешно выполнена характеристика героя '{character_info}' для пользователя {user_id}")

    except Exception as e:
        logger.error(f"Критическая ошибка при характеристике героя '{character_info}' для пользователя {user_id}: {e}", exc_info=True)
        await update.message.reply_text(
            "❌ Произошла ошибка при характеристике героя. Попробуйте отправить другую информацию."
        )
