"""Интеграция с Google Gemini API для генерации объяснений"""
import logging
from typing import Optional, Dict, Any
import google.generativeai as genai
from config import GOOGLE_API_KEY

logger = logging.getLogger(__name__)

class GeminiService:
    """Класс для работы с Google Gemini API"""

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("GOOGLE_API_KEY не установлен")

        genai.configure(api_key=api_key)

        # Настройка параметров безопасности
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            }
        ]

        # Попытка инициализации с предпочитаемой моделью
        models_to_try = ['gemini-2.5-flash', 'gemini-pro', 'gemini-pro-vision']

        self.model = None
        for model_name in models_to_try:
            try:
                self.model = genai.GenerativeModel(
                    model_name,
                    safety_settings=safety_settings
                )
                logger.info(f"Gemini API инициализирован с моделью: {model_name}")
                break
            except Exception as e:
                logger.warning(f"Не удалось инициализировать модель {model_name}: {e}")
                continue

        if self.model is None:
            raise ValueError("Не удалось инициализировать ни одну модель Gemini")

    def generate_explanation(self, prompt: str, max_tokens: int = 500) -> Optional[str]:
        """
        Сгенерировать объяснение с помощью Gemini

        Args:
            prompt (str): Запрос для генерации
            max_tokens (int): Максимальное количество токенов

        Returns:
            Optional[str]: Сгенерированное объяснение или None при ошибке
        """
        try:
            # Настраиваем параметры генерации
            generation_config = genai.types.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=0.7,
                top_p=0.8,
                top_k=40
            )

            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )

            if response and response.text:
                return response.text.strip()
            else:
                logger.warning("Gemini вернул пустой ответ")
                return None

        except Exception as e:
            logger.error(f"Ошибка при вызове Gemini API: {e}")
            return None

    def explain_word(self, word: str, context: str = "") -> Optional[str]:
        """
        Объяснить литературное слово

        Args:
            word (str): Слово для объяснения
            context (str): Дополнительный контекст из литературы

        Returns:
            Optional[str]: Объяснение слова
        """
        prompt = f"""
        Объясни литературное или устаревшее слово "{word}" простым современным языком.
        Если это слово из русской классической литературы XIX-XX веков, укажи культурный контекст.

        Структура ответа:
        Определение: [Краткое определение слова]

        Синоним: [Современный синоним или аналог]

        Пример: [Пример использования в литературе]

        Контекст: [Культурный контекст, если применимо]

        Будь краток и информативен.
        """

        if context:
            prompt += f"\n\nКонтекст: {context}"

        return self.generate_explanation(prompt)

    def explain_phrase(self, phrase: str) -> Optional[str]:
        """
        Объяснить литературную фразу или цитату

        Args:
            phrase (str): Фраза для объяснения

        Returns:
            Optional[str]: Объяснение фразы
        """
        prompt = f'''
        Объясни значение литературной фразы или выражения: "{phrase}"

        Структура ответа:
        Значение: [прямое значение фразы]

        Современный перевод: [как сказать то же самое сегодня]

        Контекст: [исторический или культурный контекст, когда и где использовалось]

        Происхождение: [откуда пошло выражение]

        Будь точен и основывайся на фактических знаниях русской литературы и языка.
        '''

        return self.generate_explanation(prompt)

    def retell_text(self, text: str, target_audience: str = "современный читатель") -> Optional[str]:
        """
        Пересказать текст современным языком

        Args:
            text (str): Исходный текст
            target_audience (str): Целевая аудитория

        Returns:
            Optional[str]: Пересказ текста
        """
        prompt = f"""
        Перескажи этот текст простым современным языком для {target_audience}.

        Исходный текст:
        "{text}"

        Инструкции:
        - Сохрани смысл и основные события
        - Используй современную лексику вместо устаревшей
        - Сократи длинные предложения
        - Удали избыточные описания, но сохрани важные детали
        - Результат должен быть в 2-3 раза короче оригинала

        Современный пересказ:
        """

        return self.generate_explanation(prompt)

    def generate_quiz_questions(self, topic: str, count: int = 3) -> Optional[list]:
        """
        Сгенерировать вопросы для викторины

        Args:
            topic (str): Тема викторины
            count (int): Количество вопросов

        Returns:
            Optional[list]: Список вопросов с вариантами ответов
        """
        prompt = f'''
        Создай {count} вопроса для викторины по теме "{topic}" из русской литературы.

        Каждый вопрос должен:
        1. Быть связан с литературными терминами, произведениями или авторами
        2. Иметь 4 варианта ответа (только один правильный)
        3. Содержать краткое объяснение правильного ответа

        Формат для каждого вопроса:
        ВОПРОС: [текст вопроса]
        A) [вариант 1]
        B) [вариант 2]
        C) [вариант 3]
        D) [вариант 4]
        ПРАВИЛЬНЫЙ: [буква правильного ответа]
        ОБЪЯСНЕНИЕ: [краткое объяснение]

        '''

        response = self.generate_explanation(prompt, max_tokens=1000)

        if response:
            return self._parse_quiz_questions(response)
        return None

    def _parse_quiz_questions(self, response: str) -> list:
        """
        Разобрать ответ API с вопросами викторины

        Args:
            response (str): Сырой ответ API

        Returns:
            list: Список структурированных вопросов
        """
        questions = []
        sections = response.split('ВОПРОС:')

        for section in sections[1:]:  # Пропускаем первую пустую часть
            try:
                lines = section.strip().split('\n')
                question_text = lines[0].strip()

                options = []
                correct_answer = ""
                explanation = ""

                for line in lines[1:]:
                    line = line.strip()
                    if line.startswith(('A)', 'B)', 'C)', 'D)')):
                        options.append(line[3:].strip())
                    elif line.startswith('ПРАВИЛЬНЫЙ:'):
                        correct_letter = line.split(':')[1].strip()
                        # Преобразуем букву в индекс
                        letter_to_index = {'A': 0, 'a': 0, 'B': 1, 'b': 1,
                                         'C': 2, 'c': 2, 'D': 3, 'd': 3}
                        correct_answer = letter_to_index.get(correct_letter, 0)
                    elif line.startswith('ОБЪЯСНЕНИЕ:'):
                        explanation = line.split(':', 1)[1].strip()

                if len(options) == 4:
                    questions.append({
                        'question': question_text,
                        'options': options,
                        'correct_index': correct_answer,
                        'explanation': explanation
                    })

            except Exception as e:
                logger.warning(f"Ошибка при разборе вопроса викторины: {e}")
                continue

        return questions

# Глобальный экземпляр сервиса (инициализируется только при необходимости)
gemini_service = None

def initialize_gemini_service():
    """Инициализировать Gemini сервис при необходимости"""
    global gemini_service
    if gemini_service is None:
        logger.info("Начинаем инициализацию Gemini API...")
        try:
            gemini_service = GeminiService(GOOGLE_API_KEY)
            logger.info("Gemini API успешно инициализирован глобально")
            return True
        except ValueError as e:
            logger.error(f"Не удалось инициализировать Gemini API: {e}")
            logger.error(f"GOOGLE_API_KEY присутствует: {bool(GOOGLE_API_KEY)}")
            gemini_service = None
            logger.warning("Бот будет работать только с предварительной базой данных")
            return False
        except Exception as e:
            logger.error(f"Неожиданная ошибка при инициализации Gemini: {e}")
            gemini_service = None
            return False
    return True

def generate_word_explanation(word: str, context: str = "") -> Optional[str]:
    """Глобальная функция для объяснения слова"""
    if gemini_service:
        return gemini_service.explain_word(word, context)
    return None

def generate_phrase_explanation(phrase: str) -> Optional[str]:
    """Глобальная функция для объяснения фразы"""
    if gemini_service:
        return gemini_service.explain_phrase(phrase)
    return None

def generate_text_retelling(text: str) -> Optional[str]:
    """Глобальная функция для пересказывания текста"""
    if gemini_service:
        return gemini_service.retell_text(text)
    return None

def generate_quiz_questions(topic: str = "русская литература", count: int = 3) -> Optional[list]:
    """Глобальная функция для генерации вопросов викторины"""
    if gemini_service:
        return gemini_service.generate_quiz_questions(topic, count)
    return None
