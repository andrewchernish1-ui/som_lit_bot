#!/usr/bin/env python3
"""Тестовый скрипт для проверки импортов и инициализации бота"""

import sys
import os

def test_imports():
    """Тестируем все импорты"""
    print("🧪 Проверка импортов...")

    try:
        # Тестируем базовые импорты
        from config import validate_config, TELEGRAM_BOT_TOKEN, GOOGLE_API_KEY
        print("✅ config.py - OK")

        from literary_data import get_word_definition, get_phrase_explanation
        print("✅ literary_data.py - OK")

        from database import DatabaseManager, save_word, get_user_dictionary
        print("✅ database.py - OK")

        # Тестируем Gemini (с плейсхолдером)
        try:
            from gemini_service import generate_word_explanation
            print("✅ gemini_service.py - OK (с плейсхолдером)")
        except Exception as e:
            print(f"⚠️ gemini_service.py - инициализация с ошибкой: {e}")

        # Тестируем обработчики
        from handlers.start_handler import start
        print("✅ handlers/start_handler.py - OK")

        from keyboards import get_main_menu_keyboard
        print("✅ keyboards.py - OK")

        from handlers.word_handler import explain_word
        print("✅ handlers/word_handler.py - OK")

        from handlers.phrase_handler import explain_phrase
        print("✅ handlers/phrase_handler.py - OK")

        from handlers.retell_handler import retell_text
        print("✅ handlers/retell_handler.py - OK")

        from handlers.dictionary_handler import show_dictionary
        print("✅ handlers/dictionary_handler.py - OK")

        from handlers.quiz_handler import start_quiz
        print("✅ handlers/quiz_handler.py - OK")

        print("\n🎉 Все основные импорты работают!")
        return True

    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        return False
    except Exception as e:
        print(f"❌ Непредвиденная ошибка: {e}")
        return False

def test_database():
    """Тестируем базу данных"""
    print("\n🗄️ Проверка базы данных...")

    try:
        from database import DatabaseManager

        db = DatabaseManager()
        print("✅ База данных инициализирована")

        # Тестируем сохранение слова
        test_user_id = 999999
        result = db.save_word(test_user_id, "исправник", "Тестовое объяснение")
        print(f"✅ Сохранение слова: {'OK' if result else 'FAILED'}")

        # Тестируем получение словаря
        words = db.get_user_dictionary(test_user_id, limit=5)
        print(f"✅ Получение словаря: {len(words)} слов")

        # Очищаем тестовые данные
        db.clear_user_dictionary(test_user_id)
        print("✅ Очистка тестовых данных")

        return True

    except Exception as e:
        print(f"❌ Ошибка базы данных: {e}")
        return False

def main():
    """Главная функция тестирования"""
    print("🚀 Запуск тестов бота Литературный Помощник\n")

    # Проверяем Python версию
    print(f"🐍 Python версия: {sys.version}")

    imports_ok = test_imports()
    db_ok = test_database()

    if imports_ok and db_ok:
        print("\n✅ Все тесты пройдены! Бот готов к работе.")
        print("💡 Для запуска используйте: python main.py")
        print("⚠️ Не забудьте заменить плейсхолдеры в .env файле на реальные API ключи")
    else:
        print("\n❌ Найдены ошибки. Проверьте код и зависимости.")
        sys.exit(1)

if __name__ == "__main__":
    main()
