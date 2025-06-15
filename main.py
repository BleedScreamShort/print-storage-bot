import telebot
import json
import os
from telebot import types

API_TOKEN = os.environ.get("API_TOKEN")
OWNER_ID = int(os.environ.get("OWNER_ID"))
DB_PATH = "database.json"

bot = telebot.TeleBot(API_TOKEN)

def load_db():
    if not os.path.exists(DB_PATH):
        return {}
    with open(DB_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_db(db):
    with open(DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

database = load_db()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Напиши название принта или пришли файл, чтобы добавить его в базу.")

@bot.message_handler(content_types=['document'])
def handle_doc(message):
    user_id = message.from_user.id
    file_name = message.document.file_name
    file_id = message.document.file_id

    if user_id != OWNER_ID:
        bot.reply_to(message, "Извините, только админ может загружать новые принты.")
        return

    if file_name in database:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Заменить", callback_data=f"replace:{file_name}:{file_id}"))
        markup.add(types.InlineKeyboardButton("Пропустить", callback_data="skip"))
        bot.send_message(user_id, f"⚠️ Принт с именем {file_name} уже существует. Заменить?", reply_markup=markup)
    else:
        database[file_name] = file_id
        save_db(database)
        bot.send_message(user_id, f"✅ Принт добавлен:\n📄 {file_name}\n🆔 {file_id}")

@bot.callback_query_handler(func=lambda call: call.data.startswith("replace") or call.data == "skip")
def callback_handler(call):
    if call.data == "skip":
        bot.answer_callback_query(call.id, "Пропущено")
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        return

    _, file_name, file_id = call.data.split(":")
    database[file_name] = file_id
    save_db(database)
    bot.edit_message_text(f"✅ Обновлено:\n📄 {file_name}\n🆔 {file_id}", call.message.chat.id, call.message.message_id)

@bot.message_handler(func=lambda msg: True, content_types=['text'])
def handle_search(message):
    query = message.text.strip()
    matches = [name for name in database if query.lower() in name.lower()]
    if not matches:
        bot.reply_to(message, "😕 Принт не найден. Попробуй другое слово.")
        return

    for name in matches:
        bot.send_document(message.chat.id, database[name], caption=name)

print("Бот запущен...")
bot.infinity_polling()
