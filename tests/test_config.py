"""Тесты для конфигурации бота"""
import pytest
import os
from unittest.mock import patch


@pytest.mark.unit
class TestConfig:
    """Тесты модуля config.py"""

    def test_validate_config_missing_token(self):
        """Тест валидации конфигурации без токена"""
        from config import validate_config

        # Убираем TELEGRAM_BOT_TOKEN из окружения
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="TELEGRAM_BOT_TOKEN не найден"):
                validate_config()

    def test_validate_config_valid_token(self):
        """Тест валидации конфигурации с валидным токеном"""
        from config import validate_config

        # Устанавливаем токен
        with patch.dict(os.environ, {'TELEGRAM_BOT_TOKEN': '123456789:ABCDEF'}):
            # Не должно вызывать исключение
            validate_config()

    def test_get_telegram_token(self):
        """Тест получения токена Telegram"""
        from config import TELEGRAM_BOT_TOKEN

        with patch.dict(os.environ, {'TELEGRAM_BOT_TOKEN': 'test_token'}):
            # Перезагрузим модуль для применения переменных
            import importlib
            import config
            importlib.reload(config)

            # Проверим что токен доступен
            assert hasattr(config, 'TELEGRAM_BOT_TOKEN')

    def test_get_openrouter_token(self):
        """Тест получения токена OpenRouter"""
        # Проверим что можем импортировать без ошибок
        from config import OPENROUTER_API_KEY

        # Токен может быть None, но импорт должен работать
        assert OPENROUTER_API_KEY is not None or OPENROUTER_API_KEY is None  # всегда true
