import time
import threading
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Вставте ваш токен від BotFather
TOKEN = "9114884868:AAF5XvZrBQ8wyA3FSz03mCYSAy5JFbqrcOY"
bot = telebot.TeleBot(TOKEN)

# Словник для зберігання налаштувань користувачів (у реальному проєкті краще використовувати Базу Даних)
user_settings = {}

# Приклад списку сервісних центрів та категорій
SERVICE_CENTERS = {
    "tsc_1241": "ТСЦ № 1241 (м. Вінниця)",
    "tsc_1242": "ТСЦ № 1242 (м. Жмеринка)"
}

CATEGORIES = {
    "cat_b": "Категорія B (легкові авто)",
    "cat_a": "Категорія A (мотоцикли)"
}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    user_settings[chat_id] = {"tsc": None, "category": None, "woodworking": False}
    
    markup = InlineKeyboardMarkup()
    for key, name in SERVICE_CENTERS.items():
        markup.add(InlineKeyboardButton(name, callback_data=f"tsc_{key}"))
    
    bot.send_message(
        chat_id, 
        "Привіт! Я допоможу знайти вільний талон на практичний іспит[cite: 1].\n\nОберіть сервісний центр:", 
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    chat_id = call.message.chat.id
    data = call.data
    
    if chat_id not in user_settings:
        user_settings[chat_id] = {"tsc": None, "category": None}

    if data.startswith("tsc_"):
        tsc_key = data.replace("tsc_tsc_", "tsc_") # очистка префікса
        user_settings[chat_id]["tsc"] = tsc_key
        
        # Далі просимо обрати категорію транспорту
        markup = InlineKeyboardMarkup()
        for key, name in CATEGORIES.items():
            markup.add(InlineKeyboardButton(name, callback_data=f"cat_{key}"))
        
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text=f"Ви обрано ТСЦ. Тепер оберіть категорію транспорту:",
            reply_markup=markup
        )
        
    elif data.startswith("cat_"):
        cat_key = data.replace("cat_", "")
        user_settings[chat_id]["category"] = cat_key
        
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text="✅ Налаштування збережено! Я почав моніторинг вільних талонів за вашими критеріями. Щойно вони з'являться, я надішлю дату та час."
        )
        
        # Запускаємо фоновий потоковий моніторинг для цього користувача
        threading.Thread(target=monitor_slots_for_user, args=(chat_id,)).start()

def monitor_slots_for_user(chat_id):
    """Функція перевірки талонів за параметрами користувача"""
    while chat_id in user_settings:
        settings = user_settings[chat_id]
        tsc = settings.get("tsc")
        category = settings.get("category")
        
        # --- ТУТ ІМПЛЕМЕНТУЄТЬСЯ ЛОГІКА SELENIUM / ЗАПИТІВ ДО API МВС ---
        # Ви передаєте змінні `tsc` та `category` у ваш Selenium-скрипт, 
        # який заходить на сайт е-запису, обирає місто/ТСЦ та категорію.
        
        slots_found = False  # Змініть на результат перевірки з сайту
        found_date_time = "15.11.2026 о 10:30" # Приклад отриманої дати і часу з сайту

        if slots_found:
            bot.send_message(
                chat_id, 
                f"🟢 **Знайдено вільний талон!**\n\n📅 Дата та час: {found_date_time}\n📍 ТСЦ: {SERVICE_CENTERS.get(tsc, 'Не вказано')}"
            )
            break # Зупиняємо моніторинг після знаходження або продовжуємо за потреби
            
        time.sleep(300) # Перевірка кожні 5 хвилин, щоб не отримати бан за спам

if __name__ == '__main__':
    bot.polling(none_stop=True)