
import os
import time
import random
import google.generativeai as genai
from datetime import datetime
import requests

def generate_post(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print("❌ Ошибка генерации текста:", e)
        return None

def insert_links(post_text, offer_link=None, promo_link=None):
    cta_templates = [
        f'👉 <a href="{offer_link}">Узнать больше</a>',
        f'🔥 <a href="{offer_link}">Получить бонус</a>',
        f'📲 <a href="{offer_link}">Открыть предложение</a>'
    ]
    promo_templates = [
        f'📢 Также рекомендую канал по трейдингу: <a href="{promo_link}">посмотреть</a>',
        f'💹 Вот канал, где я разбираю сделки в крипте: <a href="{promo_link}">подписаться</a>',
    ]

    cta = random.choice(cta_templates) if offer_link else ''
    promo = random.choice(promo_templates) if promo_link else ''
    method = random.choice(['start', 'middle', 'end'])

    if method == 'start':
        return promo + '\n\n' + post_text + '\n\n' + cta
    elif method == 'middle':
        parts = post_text.split('. ')
        if len(parts) > 2:
            insert_index = len(parts) // 2
            parts.insert(insert_index, promo)
            post_text = '. '.join(parts)
        return post_text + '\n\n' + cta
    else:
        return post_text + '\n\n' + promo + '\n\n' + cta

def send_to_telegram(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    }
    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print("✅ Текстовое сообщение отправлено.")
        else:
            print("❌ Ошибка отправки текста:", response.text)
    except Exception as e:
        print("❌ Ошибка при отправке текста:", e)

def post_once():
    print(f"🕒 Запуск публикации: {datetime.now().strftime('%H:%M:%S')}")
    prompt = os.getenv("GLOBAL_TOPIC", "Финансовая мотивация.")
    offer_link = os.getenv("OFFER_LINK")
    promo_link = os.getenv("PROMO_LINK")
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
    style = os.getenv("POST_STYLE", "дружелюбный и ободряющий стиль подачи")

    full_prompt = f"{prompt}\n\nСтиль: {style}"
    post = generate_post(full_prompt)
    if post:
        post = insert_links(post, offer_link, promo_link)
        send_to_telegram(telegram_token, telegram_chat_id, post)

if __name__ == "__main__":
    genai.configure(api_key=os.getenv("GEMINI_KEY"))
    model = genai.GenerativeModel("gemini-pro")

    print("🤖 Автопостинг-бот запущен. Публикации каждые 5 минут.")
    while True:
        post_once()
        time.sleep(300)
