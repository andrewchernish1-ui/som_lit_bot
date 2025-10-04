"""Обработчик викторины"""
from telegram import Update
from telegram.ext import ContextTypes
import logging
import random
from keyboards import get_quiz_keyboard
from database import get_user_dictionary
from openrouter_service import generate_quiz_questions
from literary_data import get_literary_terms

logger = logging.getLogger(__name__)

# Хранилище активных викторин (user_id -> правильный ответ)
active_quizzes = {}

def generate_personalized_quiz_question(user_id: int):
    """
    Генерирует персонализированный вопрос викторины на основе пользовательского словаря

    Args:
        user_id (int): ID пользователя

    Returns:
        tuple: (question, options, correct_index) или None если не удалось сгенерировать
    """
    # Получаем слова пользователя из базы данных
    user_words = get_user_dictionary(user_id, limit=20)

    if len(user_words) >= 3:
        # Если у пользователя достаточно слов, генерируем вопрос на основе них
        return generate_quiz_from_user_words(user_words)
    else:
        # Если мало слов, генерируем вопрос на основе классической литературы
        return generate_literary_quiz_question()

def generate_quiz_from_user_words(user_words):
    """
    Генерирует вопрос викторины на основе слов пользователя

    Args:
        user_words (list): Список слов пользователя

    Returns:
        tuple: (question, options, correct_index) или None
    """
    try:
        # Выбираем случайное слово для вопроса
        random_word = random.choice(user_words)
        correct_definition = random_word['explanation'][:100]  # Берем первые 100 символов объяснения

        # Создаем варианты неправильных ответов из других слов пользователя
        other_words = [w for w in user_words if w != random_word]
        wrong_options = []

        for _ in range(3):
            if other_words:
                wrong_word = random.choice(other_words)
                wrong_options.append(wrong_word['explanation'][:100])
                other_words.remove(wrong_word)
            else:
                # Если не хватает слов, используем общие литературные термины
                wrong_options.append("Общее понятие из русской литературы")

        # Перемешиваем варианты
        all_options = wrong_options + [correct_definition]
        random.shuffle(all_options)
        correct_index = all_options.index(correct_definition)

        question = f"Что означает слово '{random_word['word']}'?"

        return question, all_options, correct_index

    except Exception as e:
        logger.error(f"Ошибка при генерации вопроса из пользовательских слов: {e}")
        return None

def generate_literary_quiz_question():
    """
    Генерирует вопрос викторины на основе классической литературы

    Returns:
        tuple: (question, options, correct_index) или None
    """
    try:
        # Используем литературные термины из базы данных
        literary_terms = get_literary_terms()

        if not literary_terms:
            # Fallback на статические вопросы
            return get_fallback_quiz_question()

        # Выбираем случайный термин
        term = random.choice(literary_terms)
        correct_definition = term['definition'][:100]

        # Создаем неправильные варианты
        other_terms = [t for t in literary_terms if t != term]
        wrong_options = []

        for _ in range(3):
            if other_terms:
                wrong_term = random.choice(other_terms)
                wrong_options.append(wrong_term['definition'][:100])
                other_terms.remove(wrong_term)
            else:
                wrong_options.append("Общее литературное понятие")

        # Перемешиваем варианты
        all_options = wrong_options + [correct_definition]
        random.shuffle(all_options)
        correct_index = all_options.index(correct_definition)

        question = f"Что означает термин '{term['term']}' в русской литературе?"

        return question, all_options, correct_index

    except Exception as e:
        logger.error(f"Ошибка при генерации литературного вопроса: {e}")
        return get_fallback_quiz_question()

def get_fallback_quiz_question():
    """Возвращает fallback вопрос викторины"""
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
        logger.info(f"Пользователь {user_id} запустил викторину")

        # Получаем слова пользователя для статистики
        user_words = get_user_dictionary(user_id, limit=20)
        logger.info(f"У пользователя {user_id} в словаре {len(user_words)} слов")

        # Генерируем персонализированный вопрос
        logger.info(f"Генерируем персонализированный вопрос для пользователя {user_id}")
        quiz_data = generate_personalized_quiz_question(user_id)

        if quiz_data:
            question, options, correct_index = quiz_data
            logger.info(f"Сгенерирован персонализированный вопрос для пользователя {user_id}")
        else:
            # Fallback на простые вопросы, если не удалось сгенерировать
            logger.warning(f"Не удалось сгенерировать персонализированный вопрос для пользователя {user_id}, используем fallback")
            question, options, correct_index = get_fallback_quiz_question()

        # Сохраняем правильный ответ
        active_quizzes[user_id] = correct_index
        logger.info(f"Сохранен правильный ответ для викторины пользователя {user_id}: индекс {correct_index}")

        keyboard = get_quiz_keyboard(question, options, correct_index)

        await update.message.reply_text(
            f"❓ Викторина!\n\n{question}",
            reply_markup=keyboard
        )

        logger.info(f"Викторина успешно запущена для пользователя {user_id}")

    except Exception as e:
        logger.error(f"Критическая ошибка при запуске викторины для пользователя {user_id}: {e}", exc_info=True)
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
