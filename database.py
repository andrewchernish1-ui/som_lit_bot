"""Работа с SQLite базой данных для пользовательских словарей"""
import sqlite3
import logging
from typing import List, Dict, Optional
from config import DATABASE_PATH

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Класс для управления базой данных"""

    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        """Получить соединение с базой данных"""
        return sqlite3.connect(self.db_path)

    def init_db(self):
        """Инициализировать базу данных и создать таблицы"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Таблица пользовательских словарей
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_dictionaries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    word TEXT NOT NULL,
                    explanation TEXT NOT NULL,
                    lookup_count INTEGER DEFAULT 1,
                    first_lookup TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_lookup TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, word)
                )
            ''')

            # Таблица статистики пользователей
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_stats (
                    user_id INTEGER PRIMARY KEY,
                    total_lookups INTEGER DEFAULT 0,
                    unique_words INTEGER DEFAULT 0,
                    quiz_games INTEGER DEFAULT 0,
                    quiz_correct INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            conn.commit()
            logger.info("База данных инициализирована")

    def save_word(self, user_id: int, word: str, explanation: str) -> bool:
        """
        Сохранить слово в словарь пользователя

        Args:
            user_id (int): ID пользователя
            word (str): Слово для сохранения
            explanation (str): Объяснение слова

        Returns:
            bool: True если сохранено, False если ошибка
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Попытаться вставить новое слово или обновить счетчик существующих
                cursor.execute('''
                    INSERT INTO user_dictionaries (user_id, word, explanation, lookup_count, last_lookup)
                    VALUES (?, ?, ?, 1, CURRENT_TIMESTAMP)
                    ON CONFLICT(user_id, word) DO UPDATE SET
                        lookup_count = lookup_count + 1,
                        last_lookup = CURRENT_TIMESTAMP
                ''', (user_id, word.lower(), explanation))

                # Обновить статистику пользователя
                cursor.execute('''
                    INSERT INTO user_stats (user_id, total_lookups)
                    VALUES (?, 1)
                    ON CONFLICT(user_id) DO UPDATE SET
                        total_lookups = total_lookups + 1
                ''', (user_id,))

                # Обновить количество уникальных слов
                self._update_unique_words_count(user_id)

                conn.commit()
                return True

        except Exception as e:
            logger.error(f"Ошибка при сохранении слова '{word}' для пользователя {user_id}: {e}")
            return False

    def get_user_dictionary(self, user_id: int, limit: int = 50) -> List[Dict]:
        """
        Получить словарь пользователя

        Args:
            user_id (int): ID пользователя
            limit (int): Максимальное количество слов

        Returns:
            List[Dict]: Список слов с объяснениями
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    SELECT word, explanation, lookup_count, first_lookup, last_lookup
                    FROM user_dictionaries
                    WHERE user_id = ?
                    ORDER BY last_lookup DESC
                    LIMIT ?
                ''', (user_id, limit))

                words = []
                for row in cursor.fetchall():
                    words.append({
                        'word': row[0],
                        'explanation': row[1],
                        'lookup_count': row[2],
                        'first_lookup': row[3],
                        'last_lookup': row[4]
                    })

                return words

        except Exception as e:
            logger.error(f"Ошибка при получении словаря пользователя {user_id}: {e}")
            return []

    def clear_user_dictionary(self, user_id: int) -> bool:
        """
        Очистить словарь пользователя

        Args:
            user_id (int): ID пользователя

        Returns:
            bool: True если очищено, False если ошибка
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute('DELETE FROM user_dictionaries WHERE user_id = ?', (user_id,))
                deleted_count = cursor.rowcount

                # Обновить статистику
                if deleted_count > 0:
                    self._update_unique_words_count(user_id)

                conn.commit()
                logger.info(f"Удалено {deleted_count} слов из словаря пользователя {user_id}")
                return True

        except Exception as e:
            logger.error(f"Ошибка при очистке словаря пользователя {user_id}: {e}")
            return False

    def get_user_stats(self, user_id: int) -> Optional[Dict]:
        """
        Получить статистику пользователя

        Args:
            user_id (int): ID пользователя

        Returns:
            Optional[Dict]: Статистика пользователя
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute('SELECT * FROM user_stats WHERE user_id = ?', (user_id,))
                row = cursor.fetchone()

                if row:
                    return {
                        'user_id': row[0],
                        'total_lookups': row[1],
                        'unique_words': row[2],
                        'quiz_games': row[3],
                        'quiz_correct': row[4],
                        'created_at': row[5]
                    }
                return None

        except Exception as e:
            logger.error(f"Ошибка при получении статистики пользователя {user_id}: {e}")
            return None

    def _update_unique_words_count(self, user_id: int):
        """Обновить количество уникальных слов пользователя"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Посчитать уникальные слова
                cursor.execute('SELECT COUNT(*) FROM user_dictionaries WHERE user_id = ?', (user_id,))
                unique_count = cursor.fetchone()[0]

                # Обновить статистику
                cursor.execute('''
                    INSERT INTO user_stats (user_id, unique_words)
                    VALUES (?, ?)
                    ON CONFLICT(user_id) DO UPDATE SET
                        unique_words = ?
                ''', (user_id, unique_count, unique_count))

                conn.commit()

        except Exception as e:
            logger.error(f"Ошибка при обновлении количества уникальных слов для {user_id}: {e}")

    def export_user_dictionary_csv(self, user_id: int) -> str:
        """
        Экспортировать словарь пользователя в CSV формат

        Args:
            user_id (int): ID пользователя

        Returns:
            str: CSV текст словаря
        """
        words = self.get_user_dictionary(user_id, limit=1000)

        if not words:
            return "Словарь пуст"

        csv_lines = ["Слово,Объяснение,Количество просмотров,Первое обращение,Последнее обращение"]

        for word in words:
            line = f'"{word["word"]}","{word["explanation"].replace(chr(34), chr(34) + chr(34))}","{word["lookup_count"]}","{word["first_lookup"]}","{word["last_lookup"]}"'
            csv_lines.append(line)

        return "\n".join(csv_lines)

# Глобальный экземпляр менеджера БД
db_manager = DatabaseManager()

def save_word(user_id: int, word: str, explanation: str) -> bool:
    """Глобальная функция для сохранения слова"""
    return db_manager.save_word(user_id, word, explanation)

def get_user_dictionary(user_id: int, limit: int = 50) -> List[Dict]:
    """Глобальная функция для получения словаря"""
    return db_manager.get_user_dictionary(user_id, limit)

def clear_user_dictionary(user_id: int) -> bool:
    """Глобальная функция для очистки словаря"""
    return db_manager.clear_user_dictionary(user_id)
