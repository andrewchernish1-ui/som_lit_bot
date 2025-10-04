"""Интеграция с OpenRouter API для генерации объяснений"""
import logging
import openai
from config import OPENROUTER_API_KEY

logger = logging.getLogger(__name__)

class OpenRouterService:
    """Класс для работы с OpenRouter API"""

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY не установлен")

        self.client = openai.OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        logger.info("OpenRouter API инициализирован")

    def generate_explanation(self, prompt: str, max_tokens: int = 500) -> str:
        """
        Сгенерировать объяснение с помощью OpenRouter

        Args:
            prompt (str): Запрос для генерации
            max_tokens (int): Максимальное количество токенов

        Returns:
            str: Сгенерированное объяснение
        """
        try:
            logger.info(f"Отправляем запрос в OpenRouter API (длина промпта: {len(prompt)} символов)")

            completion = self.client.chat.completions.create(
                model="google/gemini-2.0-flash-exp:free",  # Используем Gemini 2.0 Flash через OpenRouter (бесплатная модель)
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7,
            )

            if completion.choices and completion.choices[0].message:
                response_content = completion.choices[0].message.content.strip()
                logger.info(f"OpenRouter API вернул ответ (длина: {len(response_content)} символов)")
                return response_content
            else:
                logger.warning("OpenRouter вернул пустой ответ или отсутствие choices")
                return None

        except openai.APIError as e:
            logger.error(f"Ошибка API OpenRouter: {e} (код ошибки: {getattr(e, 'code', 'unknown')})")
            return None
        except openai.RateLimitError as e:
            logger.error(f"Превышен лимит запросов OpenRouter: {e}")
            return None
        except openai.AuthenticationError as e:
            logger.error(f"Ошибка аутентификации OpenRouter: {e}")
            return None
        except Exception as e:
            logger.error(f"Неожиданная ошибка при вызове OpenRouter API: {e}", exc_info=True)
            return None

    def explain_word(self, word: str, context: str = "") -> str:
        """
        Объяснить литературное слово

        Args:
            word (str): Слово для объяснения
            context (str): Дополнительный контекст из литературы

        Returns:
            str: Объяснение слова
        """
        prompt = f"""
        Объясни литературное или устаревшее слово "{word}" простым современным языком.
        Если это слово из русской классической литературы XIX-XX веков, укажи культурный контекст.

        Формат ответа:
        📝 [Краткое определение]

        👉 [Современный синоним или аналог]

        📖 [Пример использования в литературе]

        🌍 [Культурный контекст, если применимо]

        Будь краток и информативен, используй эмодзи для структурирования.
        """

        if context:
            prompt += f"\n\nКонтекст: {context}"

        return self.generate_explanation(prompt)

    def explain_phrase(self, phrase: str) -> str:
        """
        Объяснить литературную фразу или цитату

        Args:
            phrase (str): Фраза для объяснения

        Returns:
            str: Объяснение фразы
        """
        prompt = f'''
        Объясни значение литературной фразы или выражения: "{phrase}"

        Структура ответа:
        📖 Значение: [прямое значение фразы]

        🔍 Современный перевод: [как сказать то же самое сегодня]

        📚 Контекст: [исторический или культурный контекст, когда и где использовалось]

        📝 Происхождение: [откуда пошло выражение]

        Будь точен и основывайся на фактических знаниях русской литературы и языка.
        '''

        return self.generate_explanation(prompt)

    def retell_text(self, text: str, target_audience: str = "современный читатель") -> str:
        """
        Пересказать текст современным языком

        Args:
            text (str): Исходный текст
            target_audience (str): Целевая аудитория

        Returns:
            str: Пересказ текста
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

    def generate_quiz_questions(self, topic: str, count: int = 3) -> list:
        """
        Сгенерировать вопросы для викторины

        Args:
            topic (str): Тема викторины
            count (int): Количество вопросов

        Returns:
            list: Список вопросов с вариантами ответов
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

# Глобальный экземпляр сервиса
logger.info("Начинаем инициализацию OpenRouter API...")
try:
    openrouter_service = OpenRouterService(OPENROUTER_API_KEY)
    logger.info("OpenRouter API успешно инициализирован глобально")
except ValueError as e:
    logger.error(f"Не удалось инициализировать OpenRouter API: {e}")
    logger.error(f"OPENROUTER_API_KEY присутствует: {bool(OPENROUTER_API_KEY)}")
    openrouter_service = None
    logger.warning("Бот будет работать только с предварительной базой данных")
except Exception as e:
    logger.error(f"Неожиданная ошибка при инициализации OpenRouter: {e}")
    openrouter_service = None

def generate_word_explanation(word: str, context: str = "") -> str:
    """Глобальная функция для объяснения слова"""
    if openrouter_service:
        return openrouter_service.explain_word(word, context)
    return None

def generate_phrase_explanation(phrase: str) -> str:
    """Глобальная функция для объяснения фразы"""
    if openrouter_service:
        return openrouter_service.explain_phrase(phrase)
    return None

def generate_text_retelling(text: str) -> str:
    """Глобальная функция для пересказывания текста"""
    if openrouter_service:
        return openrouter_service.retell_text(text)
    return None

def generate_quiz_questions(topic: str = "русская литература", count: int = 3) -> list:
    """Глобальная функция для генерации вопросов викторины"""
    if openrouter_service:
        return openrouter_service.generate_quiz_questions(topic, count)
    return None
