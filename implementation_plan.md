# Implementation Plan

## Overview
Создание Telegram-бота "Литературный Помощник" на Python с использованием Google Gemini для генерации объяснений литературных терминов, фраз и произведений. Бот будет помогать читателям классической литературы понимать сложные тексты через объяснение слов, разбор фраз, пересказ на современном языке и ведение личного словаря пользователя.

## Types
Определение основных типов данных для работы с литературными объяснениями, пользовательскими словарями и игровыми элементами.

- `WordExplanation`: объект с полями word (str), explanation (str), modern_synonym (str), examples (list[str]), category (str)
- `PhraseExplanation`: объект с полями phrase (str), explanation (str), cultural_context (str), modern_paraphrase (str)
- `UserDictionary`: словарь с ключами user_id (int) и значениями списком WordExplanation
- `QuizQuestion`: объект с полями question (str), correct_answer (str), wrong_answers (list[str]), explanation (str)

## Files
Создание структурированного проекта с разделением на модули для удобства сопровождения.

Новые файлы:
- `main.py`: главный файл запуска бота с обработкой команд и маршрутизацией
- `config.py`: конфигурация с токенами API и настройками базы данных
- `database.py`: работа с SQLite базой данных для пользовательских словарей
- `literary_data.py`: предварительно заполненная база литературных терминов
- `gemini_service.py`: интеграция с Google Gemini API для генерации объяснений
- `handlers/`: папка с обработчиками команд
  - `start_handler.py`: приветствие и главное меню
  - `word_handler.py`: объяснение слов
  - `phrase_handler.py`: разбор фраз и абзацев
  - `retell_handler.py`: пересказ на современном языке
  - `dictionary_handler.py`: управление личным словарем
  - `quiz_handler.py`: викторина
- `keyboards.py`: генерация клавиатур и меню
- `utils.py`: вспомогательные функции
- `requirements.txt`: зависимости проекта
- `README.md`: документация проекта
- `.env.example`: шаблон переменных окружения

## Functions
Реализация основных функций для каждого модуля бота.

Новые функции:
- `main.py`: `main()` - запуск бота, `setup_handlers()` - настройка обработчиков
- `database.py`: `init_db()` - инициализация БД, `save_word(user_id, word, explanation)` - сохранение слова, `get_user_dictionary(user_id)` - получение словаря пользователя
- `gemini_service.py`: `generate_explanation(prompt)` - генерация объяснения через Gemini, `generate_quiz_question()` - создание вопроса для викторины
- `literary_data.py`: `get_word_definition(word)` - поиск в предварительной базе, `get_phrase_explanation(phrase)` - объяснение фразы
- `handlers/word_handler.py`: `handle_word_explanation(update, context)` - обработка команды объяснения слова
- `handlers/quiz_handler.py`: `generate_quiz()` - создание викторины, `check_answer(update, context)` - проверка ответа

## Classes
Определение классов для структурирования данных и логики.

Новые классы:
- `LiteraryBot`: главный класс бота с методами инициализации и запуска
- `DatabaseManager`: класс для работы с SQLite (методы: connect, save_word, get_dictionary, close)
- `GeminiService`: класс для работы с Google Gemini API (методы: generate_explanation, generate_quiz)
- `UserDictionary`: класс для управления словарем пользователя (методы: add_word, get_words, export_pdf)

## Dependencies
Необходимые библиотеки для работы бота.

Новые пакеты:
- `python-telegram-bot` - основная библиотека для Telegram ботов
- `google-generativeai` - SDK для Google Gemini
- `sqlite3` - встроенная библиотека Python для работы с SQLite
- `python-dotenv` - загрузка переменных окружения
- `reportlab` - генерация PDF для экспорта словарей (опционально)

## Testing
Подход к тестированию функциональности бота.

Тестовые файлы:
- `tests/test_handlers.py`: тестирование обработчиков команд
- `tests/test_database.py`: тестирование работы с БД
- `tests/test_gemini.py`: тестирование интеграции с Gemini (с моками)
- `tests/test_data.py`: тестирование предварительной базы данных

Валидационные стратегии:
- Модульное тестирование основных функций
- Интеграционное тестирование взаимодействия с Telegram API
- Тестирование обработки ошибок API
- Проверка корректности генерации объяснений

## Implementation Order
Последовательность реализации для минимизации зависимостей и обеспечения работоспособности.

1. Настройка структуры проекта и базовых файлов
2. Реализация конфигурации и переменных окружения
3. Создание предварительной базы литературных данных
4. Настройка работы с SQLite базой данных
5. Интеграция с Google Gemini API
6. Реализация основных обработчиков команд
7. Создание клавиатур и пользовательского интерфейса
8. Добавление функционала личного словаря
9. Реализация системы викторины
10. Написание тестов и отладка
11. Подготовка к развертыванию на Render.com
12. Финальное тестирование и оптимизация
