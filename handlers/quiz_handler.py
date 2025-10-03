"""Обработчик викторины"""
from telegram import Update
from telegram.ext import ContextTypes
import logging
from keyboards import get_quiz_keyboard

logger = logging.getLogger(__name__)

# Хранилище активных викторин (user_id -> правильный ответ)
active_quizzes = {}

def get_sample_quiz_question():
    """Возвращает пример вопроса викторины"""
    questions = [
        {
            "question": "Что означает слово 'исправник'?",
            "correct": "Начальник уездной полиции в Российской империи",
            "wrong": ["Духовный наставник монахов", "Староста деревни", "Военный чин"]
        },
        {
            "question": "Что значит выражение 'к шапочному разбору'?",
            "correct": "В конце, под самый конец события",
            "wrong": ["К началу собрания", "В разгар спора", "Во время выборов"]
        },
        {
            "question": "Кто такой 'старец Зосима'?",
            "correct": "Духовный наставник в 'Братьях Карамазовых' Достоевского",
            "wrong": ["Главный герой 'Войны и мира'", "Антагонист 'Преступления и наказания'", "Библейский персонаж"]
        }
    ]

    import random
    q = random.choice(questions)

    # Перемешиваем варианты ответов
    options = q["wrong"] + [q["correct"]]
    random.shuffle(options)
    correct_index = options.index(q["correct"])

    return q["question"], options, correct_index

async def start_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Запускает викторину для пользователя"""
    user_id = update.effective_user.id

    try:
        question, options, correct_index = get_sample_quiz_question()

        # Сохраняем правильный ответ
        active_quizzes[user_id] = correct_index

        keyboard = get_quiz_keyboard(question, options, correct_index)

        await update.message.reply_text(
            f"❓ Викторина!\n\n{question}",
            reply_markup=keyboard
        )

    except Exception as e:
        logger.error(f"Ошибка при запуске викторины: {e}")
        await update.message.reply_text(
            "❌ Не удалось запустить викторину. Попробуйте позже."
        )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает ответы на викторину"""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    callback_data = query.data

    if not callback_data.startswith("quiz_"):
        return

    try:
        # Парсим callback_data: quiz_{selected_index}_{correct_index}
        parts = callback_data.split("_")
        selected_index = int(parts[1])
        correct_index = int(parts[2])

        # Проверяем ответ
        if selected_index == correct_index:
            result_text = "✅ Правильно! Молодец! 🎉"
        else:
            result_text = f"❌ Неправильно. Правильный ответ: вариант {correct_index + 1}"

        # Очищаем викторину пользователя
        if user_id in active_quizzes:
            del active_quizzes[user_id]

        # Отправляем результат
        await query.edit_message_text(
            f"{query.message.text}\n\n{result_text}\n\nХочешь сыграть еще раз? Нажми 🎲 Викторина в меню!"
        )

    except Exception as e:
        logger.error(f"Ошибка при обработке ответа викторины: {e}")
        await query.edit_message_text(
            "❌ Произошла ошибка при проверке ответа."
        )
