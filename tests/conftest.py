"""Общие фикстуры для тестов"""
import pytest
import os
import sys
from unittest.mock import MagicMock
from telegram import Update, User, Message, Chat
from telegram.ext import ContextTypes

# Добавляем корневую директорию в path для импортов
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def mock_update():
    """Фикстура для создания mock Update объекта"""
    update = MagicMock(spec=Update)
    update.effective_user = MagicMock(spec=User)
    update.effective_user.id = 123456789
    update.effective_user.mention_html.return_value = "@testuser"

    update.message = MagicMock(spec=Message)
    update.message.text = "test message"
    update.message.chat = MagicMock(spec=Chat)
    update.message.chat.id = 123456789
    # Создаем async mock для reply методов
    update.message.reply_text = MagicMock(return_value=None)  # sync для простоты
    update.message.reply_html = MagicMock(return_value=None)

    # Для callback_query
    update.callback_query = MagicMock()
    update.callback_query.data = "test"
    update.callback_query.answer = MagicMock(return_value=None)
    update.callback_query.message = MagicMock()
    update.callback_query.message.reply_text = MagicMock(return_value=None)

    return update


@pytest.fixture
def mock_context():
    """Фикстура для создания mock Context объекта"""
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
    return context


@pytest.fixture
def sample_word():
    """Пример слова для тестирования"""
    return "метафора"


@pytest.fixture
def sample_phrase():
    """Пример фразы для тестирования"""
    return "В человеке всё должно быть прекрасно"


@pytest.fixture
def sample_text():
    """Пример текста для пересказывания"""
    return "Однажды Чебурашка решил погулять по городу. Он встретил крокодила Гену и других друзей."


@pytest.fixture
def sample_character():
    """Пример информации о герое"""
    return "Обломов, Гончаров \"Обломов\""
