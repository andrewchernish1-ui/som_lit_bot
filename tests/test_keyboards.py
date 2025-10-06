"""Тесты для клавиатур бота"""
import pytest
from telegram import InlineKeyboardButton


@pytest.mark.unit
class TestKeyboards:
    """Тесты модуля keyboards.py"""

    def test_get_main_menu_keyboard(self):
        """Тест создания главного меню"""
        from keyboards import get_main_menu_keyboard

        keyboard = get_main_menu_keyboard()

        # Проверим структуру клавиатуры
        assert keyboard is not None
        assert hasattr(keyboard, 'keyboard')
        assert len(keyboard.keyboard) == 4  # 4 кнопки меню

        # Проверим содержание кнопок
        expected_texts = [
            "1️⃣ Объяснить слово",
            "2️⃣ Разобрать фразу/абзац",
            "3️⃣ Пересказать современным языком",
            "4️⃣ Характеристика героя"
        ]

        # Извлекаем текст из KeyboardButton объектов
        actual_texts = [row[0].text for row in keyboard.keyboard]
        assert actual_texts == expected_texts

    def test_get_response_actions_keyboard_simple(self):
        """Тест создания клавиатуры действий с кнопкой меню"""
        from keyboards import get_response_actions_keyboard

        keyboard = get_response_actions_keyboard()

        # Проверим что есть только одна кнопка
        assert keyboard is not None
        assert hasattr(keyboard, 'inline_keyboard')
        assert len(keyboard.inline_keyboard) == 1  # одна строка
        assert len(keyboard.inline_keyboard[0]) == 1  # одна кнопка

        # Проверим содержание кнопки
        button = keyboard.inline_keyboard[0][0]
        assert button.text == "📋 Меню"
        assert button.callback_data == "show_menu"

    def test_get_response_actions_keyboard_with_word(self):
        """Тест создания клавиатуры действий с передачей слова"""
        from keyboards import get_response_actions_keyboard

        keyboard = get_response_actions_keyboard(word="метафора")

        # Все равно должна быть только кнопка меню
        assert len(keyboard.inline_keyboard) == 1
        assert len(keyboard.inline_keyboard[0]) == 1

        button = keyboard.inline_keyboard[0][0]
        assert button.text == "📋 Меню"
        assert button.callback_data == "show_menu"

    def test_quiz_keyboard_generation(self):
        """Тест создания клавиатуры для викторины"""
        from keyboards import get_quiz_keyboard

        question = "Что такое метафора?"
        options = ["Переносное значение", "Прямое значение", "Рифма"]
        correct_index = 0

        keyboard = get_quiz_keyboard(question, options, correct_index)

        # Проверим количество кнопок
        assert len(keyboard.inline_keyboard) == len(options)

        # Проверим callback_data
        for i, row in enumerate(keyboard.inline_keyboard):
            assert len(row) == 1  # одна кнопка в строке
            button = row[0]
            assert button.text == options[i]
            # callback_data должен содержать индекс ответа и правильный индекс
            assert f"quiz_{i}_{correct_index}" in button.callback_data

    def test_popular_terms_keyboard(self):
        """Тест создания клавиатуры с популярными терминами"""
        from keyboards import get_popular_terms_keyboard

        keyboard = get_popular_terms_keyboard()

        # Проверим общую структуру
        assert keyboard is not None
        assert hasattr(keyboard, 'inline_keyboard')
        assert len(keyboard.inline_keyboard) > 0

        # Проверим что есть кнопки с терминами
        all_buttons = []
        for row in keyboard.inline_keyboard:
            all_buttons.extend(row)

        # Должны быть термины и специальные кнопки
        button_texts = [btn.text for btn in all_buttons]
        assert "метафора" in button_texts
        assert "метонимия" in button_texts
        assert "📖 Другие термины" in button_texts
