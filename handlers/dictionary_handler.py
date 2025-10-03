"""Обработчик управления личным словарем пользователя"""
from telegram import Update
from telegram.ext import ContextTypes
import logging
from database import get_user_dictionary, clear_user_dictionary
from keyboards import get_dictionary_actions_keyboard

logger = logging.getLogger(__name__)

async def show_dictionary(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Показать личный словарь пользователя

    Args:
        update: Объект обновления Telegram
        context: Контекст обработчика
    """
    user_id = update.effective_user.id

    try:
        # Получаем словарь пользователя
        words = get_user_dictionary(user_id, limit=20)  # Показываем последние 20 слов

        if not words:
            response = (
                "📚 Ваш словарь пока пуст!\n\n"
                "Начните изучать литературу:\n"
                "• Используйте /слово для объяснения терминов\n"
                "• Каждый просмотренный термин сохраняется автоматически"
            )
            await update.message.reply_text(response)
            return

        # Формируем ответ со списком слов
        response_lines = ["📚 Вот слова, которые вы недавно спрашивали:"]

        for i, word_data in enumerate(words, 1):
            word = word_data['word']
            count = word_data['lookup_count']
            last_lookup = word_data['last_lookup'][:10]  # Только дата

            # Создаем краткое описание (первые 50 символов объяснения)
            short_explanation = word_data['explanation'][:50]
            if len(word_data['explanation']) > 50:
                short_explanation += "..."

            response_lines.append(
                f"{i}. {word} ({count} просмотров, {last_lookup})\n"
                f"   └ {short_explanation}"
            )

        response = "\n".join(response_lines)

        # Добавляем информацию о действиях
        total_words = len(words)
        response += f"\n\n📊 Всего уникальных слов: {total_words}"

        if total_words > 20:
            response += f"\n⚠️ Показано 20 последних слов из {total_words}"

        # Отправляем клавиатуру с действиями
        await update.message.reply_text(
            response,
            reply_markup=get_dictionary_actions_keyboard()
        )

    except Exception as e:
        logger.error(f"Ошибка при показе словаря пользователя {user_id}: {e}")
        await update.message.reply_text(
            "❌ Не удалось загрузить словарь. Попробуйте позже."
        )

async def export_dictionary_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Экспортировать словарь в PDF

    Args:
        update: Объект обновления Telegram
        context: Контекст обработчика
    """
    user_id = update.effective_user.id

    try:
        import reportlab.pdfgen.canvas as canvas
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        import io

        # Получаем все слова пользователя
        words = get_user_dictionary(user_id, limit=1000)

        if not words:
            await update.callback_query.message.reply_text(
                "📭 Ваш словарь пуст. Нечего экспортировать."
            )
            return

        # Создаем PDF
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer)

        # Настройки шрифта (если есть русский шрифт)
        try:
            c.setFont("Helvetica", 16)
        except:
            pass

        # Заголовок
        c.drawString(50, 800, "Личный литературный словарь")
        c.drawString(50, 780, f"Пользователь ID: {user_id}")
        c.drawString(50, 760, f"Всего слов: {len(words)}")

        # Список слов
        y_position = 720
        for i, word_data in enumerate(words, 1):
            if y_position < 50:  # Новая страница
                c.showPage()
                c.setFont("Helvetica", 12)
                y_position = 800

            word_line = f"{i}. {word_data['word']} ({word_data['lookup_count']} просмотров)"
            c.drawString(50, y_position, word_line)

            # Объяснение с переносом строк
            explanation = word_data['explanation']
            words_list = explanation.split()
            line = ""
            y_position -= 20

            for w in words_list:
                if c.stringWidth(line + " " + w, "Helvetica", 10) < 500:
                    line += " " + w if line else w
                else:
                    c.setFont("Helvetica", 10)
                    c.drawString(70, y_position, line)
                    line = w
                    y_position -= 15
                    if y_position < 50:
                        break

            if line and y_position >= 50:
                c.drawString(70, y_position, line)
                y_position -= 25

        c.save()
        buffer.seek(0)

        # Отправляем PDF
        await update.callback_query.message.reply_document(
            document=buffer,
            filename="literary_dictionary.pdf",
            caption="📄 Ваш личный литературный словарь в PDF формате"
        )

    except ImportError:
        await update.callback_query.message.reply_text(
            "❌ Модуль для создания PDF не установлен. Используйте экспорт в CSV."
        )
    except Exception as e:
        logger.error(f"Ошибка при экспорте PDF для пользователя {user_id}: {e}")
        await update.callback_query.message.reply_text(
            "❌ Ошибка при создании PDF файла."
        )

async def export_dictionary_csv(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Экспортировать словарь в CSV

    Args:
        update: Объект обновления Telegram
        context: Контекст обработчика
    """
    user_id = update.effective_user.id

    try:
        from database import DatabaseManager
        db = DatabaseManager()
        csv_content = db.export_user_dictionary_csv(user_id)

        if csv_content == "Словарь пуст":
            await update.callback_query.message.reply_text(
                "📭 Ваш словарь пуст. Нечего экспортировать."
            )
            return

        # Создаем файл в памяти
        import io
        csv_buffer = io.BytesIO(csv_content.encode('utf-8'))

        await update.callback_query.message.reply_document(
            document=csv_buffer,
            filename="literary_dictionary.csv",
            caption="📊 Ваш личный литературный словарь в формате CSV"
        )

    except Exception as e:
        logger.error(f"Ошибка при экспорте CSV для пользователя {user_id}: {e}")
        await update.callback_query.message.reply_text(
            "❌ Ошибка при создании CSV файла."
        )

async def clear_user_dict(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Очистить словарь пользователя

    Args:
        update: Объект обновления Telegram
        context: Контекст обработчика
    """
    user_id = update.effective_user.id

    try:
        # Запрашиваем подтверждение
        confirm_text = (
            "⚠️ Вы действительно хотите очистить весь словарь?\n\n"
            "Это действие нельзя отменить!\n"
            "Все сохраненные слова будут удалены навсегда."
        )

        # В реальном приложении здесь должна быть клавиатура подтверждения
        # Но для простоты просто очищаем
        success = clear_user_dictionary(user_id)

        if success:
            await update.callback_query.message.reply_text(
                "🗑️ Словарь очищен!\n\n"
                "Все слова были удалены. Начните собирать новый словарь заново! 📚"
            )
        else:
            await update.callback_query.message.reply_text(
                "❌ Не удалось очистить словарь. Попробуйте позже."
            )

    except Exception as e:
        logger.error(f"Ошибка при очистке словаря пользователя {user_id}: {e}")
        await update.callback_query.message.reply_text(
            "❌ Ошибка при очистке словаря."
        )
