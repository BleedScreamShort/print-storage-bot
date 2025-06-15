from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import sqlite3

TOKEN = 'ТВОЙ_ТОКЕН'
bot = TeleBot(TOKEN)

# Категории принтов
categories = {
    "🏋️‍♂️ Спортзал": "Принты на тему спортзала 💪",
    "👨‍💼 Офис": "Принты для офисной жизни 🖇️",
    "🍉 Лето": "Шашлыки, пиво, жара ☀️",
    "🎩 Барбершоп": "Мужской стиль и борода ✂️",
    "💅 Красота": "Маникюр, реснички, сияем ✨"
}

# Инициализация базы
conn = sqlite3.connect("printbase.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS prints (
    name TEXT PRIMARY KEY,
    file_id TEXT
)
""")
conn.commit()

# Хендлер стартового меню
@bot.message_handler(commands=['start'])
def start_handler(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for name in categories:
        markup.add(KeyboardButton(name))
    bot.send_message(message.chat.id, "Привет! Выбери категорию принтов:", reply_markup=markup)

# Ответ по категориям
@bot.message_handler(func=lambda m: m.text in categories)
def category_handler(message):
    bot.send_message(message.chat.id, categories[message.text])

# Добавление принтов по пересылке
@bot.message_handler(content_types=['document'])
def add_file(message):
    file_name = message.document.file_name
    file_id = message.document.file_id
    cursor.execute("SELECT file_id FROM prints WHERE name = ?", (file_name,))
    row = cursor.fetchone()

    if row:
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add("🔁 Заменить", "⏭ Пропустить")
        bot.send_message(message.chat.id, f"⚠️ Принт уже есть: {file_name}\nЗаменить?", reply_markup=markup)

        @bot.message_handler(func=lambda m: m.text in ["🔁 Заменить", "⏭ Пропустить"])
        def handle_choice(choice):
            if choice.text == "🔁 Заменить":
                cursor.execute("UPDATE prints SET file_id = ? WHERE name = ?", (file_id, file_name))
                conn.commit()
                bot.send_message(message.chat.id, f"🔄 Обновлён: {file_name}")
            else:
                bot.send_message(message.chat.id, "⏭ Пропущено")
    else:
        cursor.execute("INSERT INTO prints (name, file_id) VALUES (?, ?)", (file_name, file_id))
        conn.commit()
        bot.send_message(message.chat.id, f"✅ Получено:\n📄 {file_name}\n🆔 {file_id}")

# Поиск по ключевым словам
@bot.message_handler(func=lambda m: True)
def search_prints(message):
    query = message.text.lower().replace(" ", "").replace("_", "")
    cursor.execute("SELECT name, file_id FROM prints")
    results = []
    for name, file_id in cursor.fetchall():
        simplified = name.lower().replace(" ", "").replace("_", "")
        if query in simplified:
            results.append((name, file_id))

    if results:
        for name, file_id in results:
            bot.send_document(message.chat.id, file_id, caption=name)
    else:
        bot.send_message(message.chat.id, "🤔 Принт не найден. Попробуй другое слово.")

bot.polling()
