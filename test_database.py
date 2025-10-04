#!/usr/bin/env python3
"""Тест предварительной базы данных"""

from literary_data import get_word_definition, LITERARY_TERMS

def test_database():
    """Тест работы базы данных"""
    print("Тестируем базу данных...")

    # Тест наличия слова "помещик"
    result = get_word_definition("помещик")
    if result:
        print("✅ 'помещик' найден в базе:")
        print(f"   Определение: {result['definition']}")
        print(f"   Категория: {result['category']}")
    else:
        print("❌ 'помещик' НЕ найден в базе")

    # Тест наличия слова "буди"
    result2 = get_word_definition("буди")
    if result2:
        print("✅ 'буди' найден в базе:")
        print(f"   Определение: {result2['definition']}")
    else:
        print("❌ 'буди' НЕ найден в базе")

    # Вывод общего количества слов
    total_words = len(LITERARY_TERMS)
    print(f"\n📚 Всего слов в базе: {total_words}")

    # Вывод первых 5 слов
    print("📝 Первые 5 слов в базе:")
    for i, word in enumerate(list(LITERARY_TERMS.keys())[:5]):
        print(f"   {i+1}. {word}")

if __name__ == "__main__":
    test_database()
