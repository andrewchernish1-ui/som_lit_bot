"""Тесты для обработчиков сообщений"""
import pytest
from unittest.mock import patch, MagicMock


@pytest.mark.unit
class TestMessageHandler:
    """Тесты для message_handler.py"""

    @pytest.mark.asyncio
    async def test_handle_menu_selection_word(self, mock_update, mock_context):
        """Тест выбора пункта меню - объяснение слова"""
        from handlers.message_handler import handle_menu_selection

        mock_update.message.text = "1️⃣ Объяснить слово"

        # Очистим состояния
        from handlers.message_handler import USER_STATES
        USER_STATES.clear()

        await handle_menu_selection(mock_update, mock_context, mock_update.message.text)

        # Проверим что состояние установлено
        assert USER_STATES[mock_update.effective_user.id] == 1  # STATE_WAITING_WORD

        # Проверим что отправлено сообщение
        mock_update.message.reply_text.assert_called_with("📝 Введите слово, которое нужно объяснить:")

    @pytest.mark.asyncio
    async def test_handle_menu_selection_phrase(self, mock_update, mock_context):
        """Тест выбора пункта меню - разбор фразы"""
        from handlers.message_handler import handle_menu_selection

        mock_update.message.text = "2️⃣ Разобрать фразу/абзац"

        from handlers.message_handler import USER_STATES
        USER_STATES.clear()

        await handle_menu_selection(mock_update, mock_context, mock_update.message.text)

        assert USER_STATES[mock_update.effective_user.id] == 2  # STATE_WAITING_PHRASE
        mock_update.message.reply_text.assert_called_with("📖 Отправьте мне фразу, культурное понятие или имя для объяснения:")

    @pytest.mark.asyncio
    async def test_handle_menu_selection_retell(self, mock_update, mock_context):
        """Тест выбора пункта меню - пересказ текста"""
        from handlers.message_handler import handle_menu_selection

        mock_update.message.text = "3️⃣ Пересказать современным языком"

        from handlers.message_handler import USER_STATES
        USER_STATES.clear()

        await handle_menu_selection(mock_update, mock_context, mock_update.message.text)

        assert USER_STATES[mock_update.effective_user.id] == 3  # STATE_WAITING_RETELL
        mock_update.message.reply_text.assert_called_with("🔄 Отправьте текст для пересказывания современным языком:")

    @pytest.mark.asyncio
    async def test_handle_menu_selection_character(self, mock_update, mock_context):
        """Тест выбора пункта меню - характеристика героя"""
        from handlers.message_handler import handle_menu_selection

        mock_update.message.text = "4️⃣ Характеристика героя"

        from handlers.message_handler import USER_STATES
        USER_STATES.clear()

        await handle_menu_selection(mock_update, mock_context, mock_update.message.text)

        assert USER_STATES[mock_update.effective_user.id] == 4  # STATE_WAITING_CHARACTER
        mock_update.message.reply_text.assert_called_with("🎭 Введите имя и фамилию героя, а также произведение (например: Обломов, Гончаров \"Обломов\"):")

    @pytest.mark.asyncio
    async def test_handle_menu_selection_unknown(self, mock_update, mock_context):
        """Тест обработки неизвестного выбора меню"""
        from handlers.message_handler import handle_menu_selection

        mock_update.message.text = "Неизвестная команда"

        await handle_menu_selection(mock_update, mock_context, mock_update.message.text)

        # Должен отправить сообщение с меню
        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args
        assert "Пожалуйста, выберите функцию из меню" in call_args[0][0]
        # И должна быть клавиатура
        assert 'reply_markup' in call_args[1]


@pytest.mark.unit
class TestCallbackHandler:
    """Тесты для callback_handler.py"""

    def test_show_menu_callback(self, mock_update, mock_context):
        """Тест обработки колбэка show_menu"""
        # Создание отдельного mock для callback_query
        callback_query = MagicMock()
        callback_query.data = "show_menu"
        mock_update.callback_query = callback_query

        from handlers.callback_handler import handle_callback

        handle_callback(mock_update, mock_context)

        # Проверим что ответ отправлен
        callback_query.answer.assert_called_once()

        # Проверим что отправлено сообщение с меню
        mock_update.callback_query.message.reply_text.assert_called_once_with(
            "📋 Выберите функцию из меню ниже:",
            reply_markup=mock_context.call_args  # будет объект клавиатуры
        )

    def test_unknown_callback(self, mock_update, mock_context):
        """Тест обработки неизвестного колбэка"""
        callback_query = MagicMock()
        callback_query.data = "unknown_command"
        mock_update.callback_query = callback_query

        from handlers.callback_handler import handle_callback

        handle_callback(mock_update, mock_context)

        # Все равно должен показать меню
        callback_query.answer.assert_called_once()
        mock_update.callback_query.message.reply_text.assert_called_once()


@pytest.mark.unit
class TestStartHandler:
    """Тесты для start_handler.py"""

    def test_start_command(self, mock_update, mock_context):
        """Тест команды /start"""
        from handlers.start_handler import start

        start(mock_update, mock_context)

        # Проверим что отправлено приветственное сообщение
        mock_update.message.reply_html.assert_called_once()
        call_args = mock_update.message.reply_html.call_args
        assert "Литературный Помощник" in call_args[0][0]
        assert "добро пожаловать" in call_args[0][0].lower() or "привет" in call_args[0][0].lower()

        # И что есть reply_markup (клавиатура меню)
        assert 'reply_markup' in call_args[1]


@pytest.mark.unit
class TestStateManagement:
    """Тесты управления состояниями пользователей"""

    def test_user_states_persistence(self):
        """Тест сохранения состояний пользователей"""
        from handlers.message_handler import USER_STATES, STATE_WAITING_WORD, STATE_NONE

        # Очистим состояния
        USER_STATES.clear()

        # Установим состояние
        user_id = 12345
        USER_STATES[user_id] = STATE_WAITING_WORD

        # Проверим что сохранилось
        assert USER_STATES[user_id] == STATE_WAITING_WORD

        # Сменим состояние
        USER_STATES[user_id] = STATE_NONE
        assert USER_STATES[user_id] == STATE_NONE

        # Очистим
        USER_STATES.clear()
        assert len(USER_STATES) == 0
