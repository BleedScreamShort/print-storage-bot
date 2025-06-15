import telebot
import json
import os
from telebot import types

# 🔐 Укажи свой Telegram ID (только ты можешь загружать файлы)
OWNER_ID = 123456789  # <-- замени на свой Telegram user_id
TOKEN = 'ВАШ_ТОКЕН_ТУТ'
DB_PATH = 'database.json'

bot = telebot.TeleBot(TOKEN)
database = {}

# Загрузка базы
if os.path.exists(DB_PATH):
    with open(DB_PATH, 'r', encoding='utf-8') as f:
        database = json.load(f)

# Сохранение базы
def save_database():
    with open(DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(database, f, ensure_ascii=False, indent=2)

# Фильтрация по ключевым словам
def find_prints_by_query(query):
    query = query.lower().replace(' ', '').replace('_', '')
    return {
        name: file_id
        for name, file_id in database.items()
        if query in name.lower().replace('_', '').replace(' ', '')
    }

@bot.message_handler(content_types=['document'])
def handle_file(message):
    user_id = message.from_user.id
    file_info = message.document
    file_name = file_info.file_name
    file_id = file_info.file_id

    if user_id != OWNER_ID:
        bot.reply_to(message, "⛔️ Только администратор может загружать файлы.")
        return

    if file_name in database:
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("✅ Заменить", callback_data=f"replace|{file_name}|{file_id}"),
            types.InlineKeyboardButton("❌ Пропустить", callback_data="skip")
        )
        bot.reply_to(message, f"⚠️ Принт с именем {file_name} уже существует. Что делать?", reply_markup=markup)
    else:
        database[file_name] = file_id
        save_database()
        bot.reply_to(message, f"✅ Принт сохранён:\n📄 {file_name}")

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.from_user.id != OWNER_ID:
        bot.answer_callback_query(call.id, "⛔️ Недостаточно прав.", show_alert=True)
        return

    if call.data.startswith("replace"):
        _, file_name, file_id = call.data.split('|')
        database[file_name] = file_id
        save_database()
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=f"✅ Заменено: {file_name}")
    elif call.data == "skip":
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=f"❌ Пропущено")

@bot.message_handler(func=lambda message: True)
def handle_search(message):
    results = find_prints_by_query(message.text)
    if results:
        for name, file_id in results.items():
            bot.send_document(message.chat.id, file_id, caption=name)
    else:
        bot.reply_to(message, "😕 Ничего не найдено по запросу")

print("Бот запущен...")
bot.infinity_polling()
