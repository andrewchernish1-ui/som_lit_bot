#!/usr/bin/env python3
"""Тест Open Router API с DeepSeek"""

import os
import requests
import json

def test_openrouter_api():
    """Тестируем Open Router API"""

    # Читаем API ключ из переменной окружения
    api_key = os.getenv('OPENROUTER_API_KEY')

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/andrewchernish1-ui/som_lit_bot",
        "X-Title": "Literary Assistant Bot"
    }

    payload = {
        "model": "deepseek/deepseek-chat-v3.1:free",
        "messages": [
            {
                "role": "user",
                "content": "Привет! Скажи что-нибудь на русском языке."
            }
        ],
        "max_tokens": 50
    }

    try:
        print("🔄 Отправляем запрос к Open Router API...")
        print(f"📡 URL: {url}")
        print(f"🤖 Модель: {payload['model']}")
        print(f"💬 Сообщение: {payload['messages'][0]['content']}\n")

        response = requests.post(url, headers=headers, json=payload, timeout=30)

        print(f"📊 Статус код: {response.status_code}")
        print(f"📄 Headers: {dict(response.headers)}\n")

        if response.status_code == 200:
            data = response.json()
            print("✅ УСПЕХ! API отвечает корректно")
            print(f"🤖 Ответ от DeepSeek: {data['choices'][0]['message']['content']}")
            return True
        else:
            print("❌ ОШИБКА!")
            print(f"📄 Ответ сервера: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка сети: {e}")
        return False
    except Exception as e:
        print(f"❌ Непредвиденная ошибка: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Тестируем Open Router API ключ")
    print("=" * 50)

    success = test_openrouter_api()

    print("\n" + "=" * 50)
    if success:
        print("✅ Тест ПРОЙДЕН - API ключ работает!")
    else:
        print("❌ Тест НЕ ПРОЙДЕН - проблема с API ключом")
