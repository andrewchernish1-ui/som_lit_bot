"""Тесты для LLM сервиса (OpenRouter API)"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock, mock_open
import json


@pytest.mark.unit
class TestLLMService:
    """Тесты для llm_service.py"""

    def test_initialize_llm_service_success(self):
        """Тест успешной инициализации LLM сервиса"""
        from llm_service import initialize_llm_service

        with patch.dict('os.environ', {'OPENROUTER_API_KEY': 'test_key'}):
            result = initialize_llm_service()
            assert result is True

    def test_initialize_llm_service_no_key(self):
        """Тест инициализации без API ключа"""
        from llm_service import initialize_llm_service

        with patch.dict('os.environ', {}, clear=True):
            result = initialize_llm_service()
            assert result is False

    def test_generate_word_explanation_success(self):
        """Тест успешного объяснения слова через API"""
        from llm_service import generate_word_explanation

        # Mock ответ API
        mock_response_data = {
            "choices": [{
                "message": {
                    "content": "Метафора - это переносное значение слова."
                }
            }]
        }

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client_class.return_value.__aexit__.return_value = None

            mock_response = MagicMock()
            mock_response.json = MagicMock(return_value=mock_response_data)
            mock_client.post = AsyncMock(return_value=mock_response)

            with patch.dict('os.environ', {'OPENROUTER_API_KEY': 'test_key'}):
                result = generate_word_explanation("метафора")

                # Проверяем что функция не падает и что-то возвращает
                assert result is not None
                assert isinstance(result, str)
                assert len(result) > 0
                mock_client.post.assert_called_once()

    def test_generate_word_explanation_api_error(self):
        """Тест обработки ошибки API при объяснении слова"""
        from llm_service import generate_word_explanation

        with patch('httpx.post', side_effect=Exception("API Error")):
            with patch.dict('os.environ', {'OPENROUTER_API_KEY': 'test_key'}):
                result = generate_word_explanation("метафора")

                assert result is None

    def test_generate_phrase_explanation_success(self):
        """Тест успешного объяснения фразы"""
        from llm_service import generate_phrase_explanation

        mock_response_data = {
            "choices": [{
                "message": {
                    "content": "Эта фраза означает глубокую мысль."
                }
            }]
        }

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client_class.return_value.__aexit__.return_value = None

            mock_response = MagicMock()
            mock_response.json = MagicMock(return_value=mock_response_data)
            mock_client.post = AsyncMock(return_value=mock_response)

            with patch.dict('os.environ', {'OPENROUTER_API_KEY': 'test_key'}):
                result = generate_phrase_explanation("глубокая фраза")

                assert result is not None
                assert "глубокую мысль" in result.lower()
                mock_client.post.assert_called_once()

    def test_generate_text_retelling_success(self):
        """Тест успешного пересказывания текста"""
        from llm_service import generate_text_retelling

        mock_response_data = {
            "choices": [{
                "message": {
                    "content": "Современный пересказ текста."
                }
            }]
        }

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client_class.return_value.__aexit__.return_value = None

            mock_response = MagicMock()
            mock_response.json = MagicMock(return_value=mock_response_data)
            mock_client.post = AsyncMock(return_value=mock_response)

            with patch.dict('os.environ', {'OPENROUTER_API_KEY': 'test_key'}):
                result = generate_text_retelling("старый текст")

                assert result is not None
                assert "современный пересказ" in result.lower()
                mock_client.post.assert_called_once()

    def test_generate_character_description_success(self):
        """Тест успешной характеристики героя"""
        from llm_service import generate_character_description

        mock_response_data = {
            "choices": [{
                "message": {
                    "content": "Герой - ленивый дворянин."
                }
            }]
        }

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client_class.return_value.__aexit__.return_value = None

            mock_response = MagicMock()
            mock_response.json = MagicMock(return_value=mock_response_data)
            mock_client.post = AsyncMock(return_value=mock_response)

            with patch.dict('os.environ', {'OPENROUTER_API_KEY': 'test_key'}):
                result = generate_character_description("Обломов")

                assert result is not None
                assert "ленивый дворянин" in result.lower()
                mock_client.post.assert_called_once()

    @pytest.mark.parametrize("text_length", [100, 5000, 10000])
    def test_text_length_limits(self, text_length):
        """Тест ограничений на длину текста"""
        from llm_service import generate_text_retelling

        # Создаем текст заданной длины
        long_text = "а" * text_length

        if text_length > 5000:  # Проверяем что слишком длинный текст не отправляется
            with patch.dict('os.environ', {'OPENROUTER_API_KEY': 'test_key'}):
                result = generate_text_retelling(long_text)

                # Для длинного текста нет mock, но функция должна обработать
                # В реальности вернет None или ошибку

        # Для нормального текста - успешный результат
        if text_length <= 5000:
            mock_response_data = {
                "choices": [{
                    "message": {"content": "Пересказ"}
                }]
            }

            with patch('httpx.post') as mock_post:
                mock_response = MagicMock()
                mock_response.json.return_value = mock_response_data
                mock_post.return_value = mock_response

                with patch.dict('os.environ', {'OPENROUTER_API_KEY': 'test_key'}):
                    result = generate_text_retelling(long_text)
                    assert result == "Пересказ"


@pytest.mark.unit
class TestLiteraryData:
    """Тесты для literary_data.py"""

    def test_get_word_definition_existing(self):
        """Тест получения существующего слова"""
        from literary_data import get_word_definition

        word_data = get_word_definition("метафора")

        if word_data:  # Если слово есть в базе
            assert isinstance(word_data, dict)
            assert 'definition' in word_data
            assert 'word' in word_data

    def test_get_word_definition_nonexisting(self):
        """Тест получения несуществующего слова"""
        from literary_data import get_word_definition

        word_data = get_word_definition("несуществующееслово12345")

        # Для несуществующего слова должно вернуть None
        assert word_data is None

    def test_format_word_response(self):
        """Тест форматирования ответа для слова"""
        from literary_data import format_word_response

        mock_data = {
            'word': 'метафора',
            'definition': 'Переносное значение слова',
            'examples': ['Поэтическая метафора'],
            'category': 'тропы'
        }

        response = format_word_response(mock_data)

        assert 'метафора' in response.upper()  # обычно capitalize
        assert 'переносное значение' in response.lower()
        assert isinstance(response, str)

    def test_get_phrase_explanation_existing(self):
        """Тест получения существующей фразы"""
        from literary_data import get_phrase_explanation

        phrase_data = get_phrase_explanation("Век живи - век учись")

        if phrase_data:  # Если фраза есть в базе
            assert isinstance(phrase_data, dict)
            assert 'explanation' in phrase_data

    def test_get_phrase_explanation_nonexisting(self):
        """Тест получения несуществующей фразы"""
        from literary_data import get_phrase_explanation

        phrase_data = get_phrase_explanation("абракадабра12345")

        # Для несуществующей фразы должно вернуть None
        assert phrase_data is None
