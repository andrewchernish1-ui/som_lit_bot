# Тесты для Литературного Помощника

## Обзор

Этот набор тестов обеспечивает надежность и стабильность бота "Литературный Помощник". Тесты покрывают все основные компоненты:

- Конфигурацию и валидацию
- Работа с клавиатурами и меню
- Обработчики сообщений и команд
- Интеграция с API OpenRouter
- Обработка ошибок и edge cases
- Полный цикл работы бота

## Структура тестов

```
tests/
├── __init__.py              # Метка пакета
├── conftest.py              # Общие фикстуры
├── test_config.py           # Тесты конфигурации
├── test_keyboards.py        # Тесты клавиатур и меню
├── test_handlers.py         # Тесты обработчиков сообщений
├── test_llm_service.py      # Тесты API интеграции
├── test_integration.py      # Интеграционные и нагрузочные тесты
└── README.md               # Эта документация
```

## Запуск тестов

### Все тесты
```bash
pytest
```

### Только unit-тесты
```bash
pytest -m unit
```

### Только интеграционные тесты
```bash
pytest -m integration
```

### С покрытием кода
```bash
pytest --cov=src --cov-report=html
```

### С подробным выводом
```bash
pytest -v
```

### Запуск конкретного теста
```bash
pytest tests/test_config.py::TestConfig::test_validate_config_missing_token
```

## Категории тестов

### 🔧 Unit-тесты (`unit`)
Тестируют отдельные функции и методы:
- Валидация конфигурации
- Создание клавиатур
- Форматирование ответов
- Работа с локальной базой данных

### 🔗 Integration-тесты (`integration`)
Тестируют взаимодействие компонентов:
- Полный цикл обработки сообщений
- Интеграция с API
- Многошаговые сценарии

### 📡 API-тесты (`api`)
Тестируют внешние интеграции:
- OpenRouter API
- Обработка ответов API
- Обработка ошибок API

### 📱 Telegram-тесты (`telegram`)
Тестируют Telegram-специфику:
- Формат сообщений
- Клавиатуры и колбэки
- Обработка команд

### ⏱️ Slow-тесты (`slow`)
Нагрузочные тесты, которые занимают много времени.

## Фикстуры

### `mock_update`
Стандартный mock для Telegram Update объекта с предустановленными атрибутами.

### `mock_context`
Mock для ContextTypes.DEFAULT_TYPE.

### `sample_word`, `sample_phrase`, `sample_text`, `sample_character`
Примеры входных данных для тестирования.

## Написание новых тестов

### Unit-тест
```python
@pytest.mark.unit
def test_my_function():
    from my_module import my_function

    result = my_function("test_input")
    assert result == "expected_output"
```

### Тест с мокингом API
```python
def test_api_call(mock_update):
    mock_response_data = {"choices": [{"message": {"content": "OK"}}]}

    with patch('httpx.post') as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_post.return_value = mock_response

        with patch.dict('os.environ', {'OPENROUTER_API_KEY': 'test'}):
            from handlers.word_handler import explain_word
            explain_word(mock_update, MagicMock(), "word")

            mock_update.message.reply_text.assert_called()
```

## CI/CD

Для автоматического тестирования можно добавить в GitHub Actions:

```yaml
- name: Run tests
  run: |
    pip install -r requirements.txt
    pytest --cov --cov-report=xml
```

## Ожидаемые результаты

При успешном прохождении всех тестов:
- ✅ Конфигурация правильно валидируется
- ✅ Клавиатуры создаются корректно
- ✅ Все обработчики работают без ошибок
- ✅ API интеграция стабильна
- ✅ Бот обрабатывает различные сценарии
- ✅ Ошибки корректно обрабатываются

## Добавление новых тестов

1. Создайте новый файл `test_*.py`
2. Используйте маркеры `@pytest.mark.*` для категоризации
3. Добавьте фикстуры в `conftest.py` если нужно
4. Запустите тесты: `pytest tests/test_*.py`

## Полезные команды для отладки

```bash
# Показать все тесты
pytest --collect-only

# Запуск с подробностями
pytest -v -s

# Остановить на первой ошибке
pytest --tb=short --maxfail=1

# Показать покрытие для конкретного модуля
pytest --cov=handlers --cov-report=html
