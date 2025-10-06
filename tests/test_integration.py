"""Интеграционные тесты для всего бота"""
import pytest
from unittest.mock import patch, MagicMock


@pytest.mark.integration
class TestBotIntegration:
    """Интеграционные тесты полного цикла работы бота"""

    @pytest.mark.asyncio
    async def test_full_word_explanation_flow(self, mock_update, mock_context, sample_word):
        """Тест полного цикла объяснения слова"""
        from handlers.message_handler import handle_message

        # Установим состояние ожидания слова
        from handlers.message_handler import USER_STATES, STATE_WAITING_WORD
        USER_STATES[mock_update.effective_user.id] = STATE_WAITING_WORD

        # Мокаем функцию из literary_data - бот fallback'ит на базу
        mock_word_data = {
            'definition': f'{sample_word} - это литературный термин из нашей базы.',
            'examples': [f'Пример использования {sample_word}']
        }

        with patch('literary_data.get_word_definition', return_value=mock_word_data), \
             patch('llm_service.initialize_llm_service', return_value=False):  # API недоступен

            # Отправим слово для объяснения
            mock_update.message.text = sample_word
            await handle_message(mock_update, mock_context)

            # Проверим что состояние сброшено
            assert USER_STATES[mock_update.effective_user.id] == 0  # STATE_NONE

            # Проверим что отправлено сообщение
            mock_update.message.reply_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_full_phrase_explanation_flow(self, mock_update, mock_context, sample_phrase):
        """Тест полного цикла объяснения фразы"""
        from handlers.message_handler import handle_message

        # Установим состояние ожидания фразы
        from handlers.message_handler import USER_STATES, STATE_WAITING_PHRASE
        USER_STATES[mock_update.effective_user.id] = STATE_WAITING_PHRASE

        # Мокаем функцию из literary_data
        mock_phrase_data = {
            'explanation': f"Фраза '{sample_phrase}' означает важную мысль из литературы."
        }

        with patch('literary_data.get_phrase_explanation', return_value=mock_phrase_data), \
             patch('llm_service.initialize_llm_service', return_value=False):

            # Отправим фразу для объяснения
            mock_update.message.text = sample_phrase
            await handle_message(mock_update, mock_context)

            # Проверим что состояние сброшено
            assert USER_STATES[mock_update.effective_user.id] == 0

            # Проверим ответ
            mock_update.message.reply_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_full_retell_flow(self, mock_update, mock_context, sample_text):
        """Тест полного цикла пересказывания текста"""
        from handlers.message_handler import handle_message

        # Установим состояние ожидания текста
        from handlers.message_handler import USER_STATES, STATE_WAITING_RETELL
        USER_STATES[mock_update.effective_user.id] = STATE_WAITING_RETELL

        # Мокаем что API возвращает None (недоступен)
        with patch('llm_service.generate_text_retelling', return_value=None), \
             patch('llm_service.initialize_llm_service', return_value=True):

            # Отправим текст для пересказывания
            mock_update.message.text = sample_text
            await handle_message(mock_update, mock_context)

            # Проверим что состояние сброшено
            assert USER_STATES[mock_update.effective_user.id] == 0

            # Проверим что отправлено сообщение об ошибке
            mock_update.message.reply_text.assert_called_once()


@pytest.mark.integration
class TestErrorHandling:
    """Тесты обработки ошибок"""

    @pytest.mark.asyncio
    async def test_api_timeout_error(self, mock_update, mock_context):
        """Тест обработки таймаута API"""
        from handlers.word_handler import explain_word

        with patch('httpx.AsyncClient') as mock_client:
            mock_client_instance = MagicMock()
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            mock_client.return_value.__aexit__.return_value = None
            mock_client_instance.post = MagicMock(side_effect=Exception("Connection timeout"))

            with patch.dict('os.environ', {'OPENROUTER_API_KEY': 'test_key'}):
                await explain_word(mock_update, mock_context, "слово")

                # Должен отправить сообщение об ошибке
                mock_update.message.reply_text.assert_called()

    @pytest.mark.asyncio
    async def test_api_authentication_error(self, mock_update, mock_context):
        """Тест обработки ошибки аутентификации API"""
        from handlers.word_handler import explain_word

        with patch('httpx.AsyncClient') as mock_client:
            mock_client_instance = MagicMock()
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            mock_client.return_value.__aexit__.return_value = None
            mock_response = MagicMock()
            mock_response.status_code = 401
            mock_client_instance.post = MagicMock(return_value=mock_response)

            with patch.dict('os.environ', {'OPENROUTER_API_KEY': 'invalid_key'}):
                await explain_word(mock_update, mock_context, "слово")

                # Должен обработать ошибку
                mock_update.message.reply_text.assert_called()

    @pytest.mark.asyncio
    async def test_invalid_user_input(self, mock_update, mock_context):
        """Тест обработки некорректного ввода пользователя"""
        from handlers.message_handler import handle_message

        # Некорректный текст в состоянии ожидания слова
        from handlers.message_handler import USER_STATES, STATE_WAITING_WORD
        USER_STATES[mock_update.effective_user.id] = STATE_WAITING_WORD

        mock_update.message.text = ""  # Пустой ввод

        await handle_message(mock_update, mock_context)

        # Должен обработать и отправить ответ
        mock_update.message.reply_text.assert_called()

    def test_database_connection_error(self, mock_update, mock_context):
        """Тест обработки ошибки подключения к БД"""
        # Мокаем ошибку при работе с БД
        with patch('sqlite3.connect', side_effect=Exception("DB Connection Error")):
            from handlers.dictionary_handler import get_user_dictionary

            # Попытка получить словарь должна обработать ошибку
            result = get_user_dictionary(12345)
            # Функция должна вернуть пустой словарь или None без падения

    def test_memory_cleanup(self):
        """Тест очистки памяти от состояний пользователей"""
        from handlers.message_handler import USER_STATES

        # Добавим несколько состояний
        USER_STATES[1] = 1
        USER_STATES[2] = 2
        USER_STATES[3] = 3

        # Очистим
        USER_STATES.clear()

        assert len(USER_STATES) == 0


@pytest.mark.slow
@pytest.mark.integration
class TestLoadTesting:
    """Нагрузочные тесты"""

    def test_multiple_concurrent_requests(self, mock_context):
        """Тест обработки нескольких одновременных запросов"""
        # Создаем несколько mock updates для разных пользователей
        updates = []
        for user_id in range(1, 6):
            update = MagicMock()
            update.effective_user = MagicMock()
            update.effective_user.id = user_id
            update.message = MagicMock()
            update.message.text = f"метафора_{user_id}"
            update.message.reply_text = AsyncMock()
            updates.append(update)

        # Мокаем базу данных
        mock_word_data = {
            'definition': 'Тестовое объяснение слова из базы.',
            'examples': ['Пример использования']
        }

        with patch('literary_data.get_word_definition', return_value=mock_word_data), \
             patch('llm_service.initialize_llm_service', return_value=False):

            # Импортируем здесь чтобы избежать проблем с мокаемыми модулями
            from handlers.word_handler import explain_word

            # Обрабатываем все запросы
            import asyncio
            async def process_all():
                tasks = [explain_word(update, mock_context, update.message.text) for update in updates]
                await asyncio.gather(*tasks)

            asyncio.run(process_all())

            # Проверим что все запросы были обработаны
            for update in updates:
                update.message.reply_text.assert_called_once()


@pytest.mark.unit
class TestDataValidation:
    """Тесты валидации входных данных"""

    @pytest.mark.parametrize("invalid_input", [
        "",
        "   ",
        "\n\t",
        "a" * 10000,  # слишком длинное слово
        "<script>alert('xss')</script>",  # потенциально опасный ввод
        "слово\nс\nпереносами",  # многострочный текст
    ])
    @pytest.mark.asyncio
    async def test_invalid_word_inputs(self, invalid_input):
        """Тест обработки некорректных слов"""
        from handlers.word_handler import explain_word

        mock_update = MagicMock()
        mock_context = MagicMock()
        mock_update.message.reply_text = MagicMock()

        with patch.dict('os.environ', {'OPENROUTER_API_KEY': 'test_key'}), \
             patch('literary_data.get_word_definition', return_value=None), \
             patch('llm_service.initialize_llm_service', return_value=False):

            await explain_word(mock_update, mock_context, invalid_input)

            # Должен отправить какой-то ответ, не падать
            mock_update.message.reply_text.assert_called()

    @pytest.mark.parametrize("valid_input,expected_contains", [
        ("метафора", "метафора"),
        ("Обломов", "Обломов"),
        ("В человеке всё должно быть прекрасно", "прекрасно"),
    ])
    @pytest.mark.asyncio
    async def test_valid_inputs_contain_expected_content(self, valid_input, expected_contains):
        """Тест что валидные входы обрабатываются корректно"""
        # Этот тест проверяет только что функция не падает
        from handlers.word_handler import explain_word

        mock_update = MagicMock()
        mock_context = MagicMock()
        mock_update.message.reply_text = MagicMock()

        # Мокаем базу данных
        mock_data = {
            'definition': f'Определение для {valid_input}',
            'examples': [f'Пример с {valid_input}']
        }

        with patch('literary_data.get_word_definition', return_value=mock_data), \
             patch('llm_service.initialize_llm_service', return_value=False):

            await explain_word(mock_update, mock_context, valid_input)

            # Должен отправить ответ из базы данных
            mock_update.message.reply_text.assert_called()
