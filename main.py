import os
import json
import telebot
from flask import Flask, request

API_TOKEN = os.environ.get('API_TOKEN')
OWNER_ID = str(os.environ.get('OWNER_ID'))

bot = telebot.TeleBot(API_TOKEN)
server = Flask(__name__)

# Путь к базе
STORAGE_PATH = 'storage.json'

def load_storage():
    if not os.path.exists(STORAGE_PATH):
        with open(STORAGE_PATH, 'w') as f:
            json.dump({}, f)
    with open(STORAGE_PATH, 'r') as f:
        return json.load(f)

def save_storage(data):
    with open(STORAGE_PATH, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

storage = load_storage()


# === Обработка команды /start ===
@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_message(message.chat.id, "\U0001F4E3 Бот готов. Просто отправь название принта.")


# === Обработка документов (скрепка) ===
@bot.message_handler(content_types=['document'])
def handle_document(message):
    if str(message.from_user.id) != OWNER_ID:
        return
    
    doc = message.document
    file_id = doc.file_id
    file_name = doc.file_name

    storage[file_name] = file_id
    save_storage(storage)

    bot.reply_to(message, f"✅ Получено: `{file_name}`\n🆔 `{file_id}`", parse_mode='Markdown')


# === Обработка фото (если нужно) ===
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    if str(message.from_user.id) != OWNER_ID:
        return

    file_id = message.photo[-1].file_id
    file_name = f"photo_{message.message_id}.jpg"

    storage[file_name] = file_id
    save_storage(storage)

    bot.reply_to(message, f"✅ Получено: `{file_name}`\n🆔 `{file_id}`", parse_mode='Markdown')


# === Поиск по названию ===
@bot.message_handler(func=lambda m: True, content_types=['text'])
def find_print(message):
    query = message.text.strip()

    for file_name in storage:
        if query.lower() in file_name.lower():
            bot.send_document(message.chat.id, storage[file_name], caption=file_name)
            return

    bot.send_message(message.chat.id, "🤔 Принт не найден. Попробуй другое слово.")


# === Webhook ===
@server.route(f"/{API_TOKEN}", methods=['POST'])
def webhook():
    json_str = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "!", 200

@server.route("/")
def index():
    return "Бот работает ✅"

if __name__ == '__main__':
    webhook_url = f"https://print-storage-bot.onrender.com/{API_TOKEN}"
    bot.remove_webhook()
    bot.set_webhook(url=webhook_url)
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
