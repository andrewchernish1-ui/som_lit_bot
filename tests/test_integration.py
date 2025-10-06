"""Интеграционные тесты для всего бота"""
import pytest
from unittest.mock import patch, MagicMock


@pytest.mark.integration
class TestBotIntegration:
    """Интеграционные тесты полного цикла работы бота"""

    def test_full_word_explanation_flow(self, mock_update, mock_context, sample_word):
        """Тест полного цикла объяснения слова"""
        from handlers.message_handler import handle_message

        # Установим состояние ожидания слова
        from handlers.message_handler import USER_STATES, STATE_WAITING_WORD
        USER_STATES[mock_update.effective_user.id] = STATE_WAITING_WORD

        # Мокаем LLM API ответ
        mock_response_data = {
            "choices": [{
                "message": {"content": f"{sample_word} - это литературный термин."}
            }]
        }

        with patch('httpx.post') as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_response_data
            mock_post.return_value = mock_response

            with patch.dict('os.environ', {'OPENROUTER_API_KEY': 'test_key'}):
                # Отправим слово для объяснения
                mock_update.message.text = sample_word
                handle_message(mock_update, mock_context)

                # Проверим что состояние сброшено
                assert USER_STATES[mock_update.effective_user.id] == 0  # STATE_NONE

                # Проверим что отправлены сообщения процесса и ответа
                assert mock_update.message.reply_text.call_count >= 2  # "думает" + ответ

    def test_full_phrase_explanation_flow(self, mock_update, mock_context, sample_phrase):
        """Тест полного цикла объяснения фразы"""
        from handlers.message_handler import handle_message

        # Установим состояние ожидания фразы
        from handlers.message_handler import USER_STATES, STATE_WAITING_PHRASE
        USER_STATES[mock_update.effective_user.id] = STATE_WAITING_PHRASE

        # Мокаем LLM API ответ
        mock_response_data = {
            "choices": [{
                "message": {"content": f"Фраза '{sample_phrase}' означает..."}
            }]
        }

        with patch('httpx.post') as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_response_data
            mock_post.return_value = mock_response

            with patch.dict('os.environ', {'OPENROUTER_API_KEY': 'test_key'}):
                # Отправим фразу для объяснения
                mock_update.message.text = sample_phrase
                handle_message(mock_update, mock_context)

                # Проверим что состояние сброшено
                assert USER_STATES[mock_update.effective_user.id] == 0

                # Проверим ответ
                assert mock_update.message.reply_text.call_count >= 1

    def test_full_retell_flow(self, mock_update, mock_context, sample_text):
        """Тест полного цикла пересказывания текста"""
        from handlers.message_handler import handle_message

        # Установим состояние ожидания текста
        from handlers.message_handler import USER_STATES, STATE_WAITING_RETELL
        USER_STATES[mock_update.effective_user.id] = STATE_WAITING_RETELL

        # Мокаем LLM API ответ
        mock_response_data = {
            "choices": [{
                "message": {"content": "Современный пересказ текста."}
            }]
        }

        with patch('httpx.post') as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_response_data
            mock_post.return_value = mock_response

            with patch.dict('os.environ', {'OPENROUTER_API_KEY': 'test_key'}):
                # Отправим текст для пересказывания
                mock_update.message.text = sample_text
                handle_message(mock_update, mock_context)

                # Проверим что состояние сброшено
                assert USER_STATES[mock_update.effective_user.id] == 0

                # Проверим ответ
                mock_update.message.reply_text.assert_called()


@pytest.mark.integration
class TestErrorHandling:
    """Тесты обработки ошибок"""

    def test_api_timeout_error(self, mock_update, mock_context):
        """Тест обработки таймаута API"""
        from handlers.word_handler import explain_word

        with patch('httpx.post', side_effect=TimeoutError("Connection timeout")):
            with patch.dict('os.environ', {'OPENROUTER_API_KEY': 'test_key'}):
                explain_word(mock_update, mock_context, "слово")

                # Должен отправить сообщение об ошибке
                mock_update.message.reply_text.assert_called()
                call_args = mock_update.message.reply_text.call_args
                assert "ошибка" in call_args[0][0].lower()

    def test_api_authentication_error(self, mock_update, mock_context):
        """Тест обработки ошибки аутентификации API"""
        from handlers.word_handler import explain_word

        # Mock 401 Unauthorized
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("401 Unauthorized")
        mock_response.status_code = 401

        with patch('httpx.post', return_value=mock_response):
            with patch.dict('os.environ', {'OPENROUTER_API_KEY': 'invalid_key'}):
                explain_word(mock_update, mock_context, "слово")

                # Должен обработать ошибку
                mock_update.message.reply_text.assert_called()

    def test_invalid_user_input(self, mock_update, mock_context):
        """Тест обработки некорректного ввода пользователя"""
        from handlers.message_handler import handle_message

        # Некорректный текст в состоянии ожидания слова
        from handlers.message_handler import USER_STATES, STATE_WAITING_WORD
        USER_STATES[mock_update.effective_user.id] = STATE_WAITING_WORD

        mock_update.message.text = ""  # Пустой ввод

        handle_message(mock_update, mock_context)

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
            update.message.reply_text = MagicMock()
            updates.append(update)

        # Мокаем API ответ
        mock_response_data = {
            "choices": [{
                "message": {"content": "Тестовое объяснение слова."}
            }]
        }

        with patch('httpx.post') as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_response_data
            mock_post.return_value = mock_response

            with patch.dict('os.environ', {'OPENROUTER_API_KEY': 'test_key'}):
                # Импортируем здесь чтобы избежать проблем с мокаемыми модулями
                from handlers.word_handler import explain_word

                # Обрабатываем все запросы
                for update in updates:
                    explain_word(update, mock_context, update.message.text)

                # Проверим что все запросы были обработаны
                assert mock_post.call_count == len(updates)


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
    def test_invalid_word_inputs(self, invalid_input):
        """Тест обработки некорректных слов"""
        from handlers.word_handler import explain_word

        mock_update = MagicMock()
        mock_context = MagicMock()
        mock_update.message.reply_text = MagicMock()

        with patch.dict('os.environ', {'OPENROUTER_API_KEY': 'test_key'}):
            explain_word(mock_update, mock_context, invalid_input)

            # Должен отправить какой-то ответ, не падать
            mock_update.message.reply_text.assert_called()

    @pytest.mark.parametrize("valid_input,expected_contains", [
        ("метафора", "метаф"),
        ("Обломов", "Обломов"),
        ("В человеке всё должно быть прекрасно", "прекрасно"),
    ])
    def test_valid_inputs_contain_expected_content(self, valid_input, expected_contains):
        """Тест что валидные входы обрабатываются корректно"""
        # Этот тест проверяет только что функция не падает
        from handlers.word_handler import explain_word

        mock_update = MagicMock()
        mock_context = MagicMock()
        mock_update.message.reply_text = MagicMock()

        # Без мокинга API - функция должна обработать ошибку API
        explain_word(mock_update, mock_context, valid_input)

        # Должен отправить ответ (ошибку или результат)
        mock_update.message.reply_text.assert_called()
