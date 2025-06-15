import os
import sqlite3
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = '7237914704:AAGCgfYcBvNurGqC4Q1ZjFYdNZLbZdVKZ_I'
bot = telebot.TeleBot(TOKEN)

# Создаём или подключаемся к базе данных
conn = sqlite3.connect('prints.db', check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS prints (
        name TEXT PRIMARY KEY,
        file_id TEXT NOT NULL
    )
''')
conn.commit()

# Кнопки категорий (можно не менять пока)
categories = {
    "🏋️‍♂️ Спортзал": "Принты на тему спортзала 💪",
    "👨‍💼 Офис": "Принты для офисной жизни 💼",
    "🍉 Лето": "Шашлык, пиво, жара ☀️",
    "🧔‍♂️ Барбершоп": "Мужской стиль ✂️",
    "💅 Красота": "Маникюр, реснички ✨"
}

# /start
@bot.message_handler(commands=['start'])
def start_handler(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for category in categories:
        markup.add(KeyboardButton(category))
    bot.send_message(message.chat.id, "Привет! Перешли сюда принт или введи ключевое слово:", reply_markup=markup)

# Категории (пока просто текст)
@bot.message_handler(func=lambda msg: msg.text in categories)
def category_handler(message):
    bot.send_message(message.chat.id, categories[message.text])

# Обработка изображений и документов с file_id
@bot.message_handler(content_types=['photo', 'document'])
def handle_file(message):
    file_id = message.document.file_id if message.document else message.photo[-1].file_id
    file_name = message.document.file_name if message.document else "photo_from_chat"
    name_key = os.path.splitext(file_name)[0].lower().replace(' ', '_')

    cursor.execute("SELECT file_id FROM prints WHERE name = ?", (name_key,))
    row = cursor.fetchone()

    if row:
        # Если уже есть, спросим: заменить или пропустить
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("🔁 Заменить", callback_data=f"replace:{name_key}:{file_id}"),
            InlineKeyboardButton("⏭ Пропустить", callback_data="skip")
        )
        bot.send_message(message.chat.id, f"Принт `{name_key}` уже существует. Что сделать?", reply_markup=markup, parse_mode="Markdown")
    else:
        cursor.execute("INSERT INTO prints (name, file_id) VALUES (?, ?)", (name_key, file_id))
        conn.commit()
        bot.send_message(message.chat.id, f"✅ Добавлено: `{name_key}`", parse_mode="Markdown")

# Кнопки выбора: заменить или пропустить
@bot.callback_query_handler(func=lambda call: call.data.startswith("replace") or call.data == "skip")
def callback_replace(call):
    if call.data == "skip":
        bot.answer_callback_query(call.id, "Пропущено ✅")
        return

    _, name_key, new_file_id = call.data.split(":")
    cursor.execute("UPDATE prints SET file_id = ? WHERE name = ?", (new_file_id, name_key))
    conn.commit()
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=f"🔁 Обновлено: `{name_key}`", parse_mode="Markdown")

# Поиск по ключевым словам
@bot.message_handler(func=lambda msg: True)
def search_handler(message):
    query = message.text.lower().replace(" ", "_")
    cursor.execute("SELECT name, file_id FROM prints WHERE name LIKE ?", (f"%{query}%",))
    result = cursor.fetchone()

    if result:
        bot.send_photo(message.chat.id, result[1], caption=f"🔎 Найдено: {result[0]}")
    else:
        bot.send_message(message.chat.id, "😕 Принт не найден. Попробуй другое слово.")

bot.polling(none_stop=True)
