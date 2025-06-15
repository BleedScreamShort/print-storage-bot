import os
import json
import telebot
from flask import Flask, request
from telebot.types import Message

API_TOKEN = os.environ.get("API_TOKEN")
OWNER_ID = int(os.environ.get("OWNER_ID"))

bot = telebot.TeleBot(API_TOKEN)
server = Flask(__name__)

DB_PATH = "database.json"
if not os.path.exists(DB_PATH):
    with open(DB_PATH, 'w', encoding='utf-8') as f:
        json.dump({}, f, ensure_ascii=False)

def load_db():
    with open(DB_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_db(data):
    with open(DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

@bot.message_handler(content_types=['document'])
def handle_doc(msg: Message):
    if msg.from_user.id != OWNER_ID:
        bot.reply_to(msg, "⛔ Только владелец может загружать принты")
        return

    file_info = msg.document
    file_id = file_info.file_id
    name = file_info.file_name

    db = load_db()
    db[name] = file_id
    save_db(db)

    bot.reply_to(msg, f"✅ Получено:\n📁 <b>{name}</b>\n🪪 <code>{file_id}</code>", parse_mode='HTML')

@bot.message_handler(content_types=['text'])
def handle_search(msg: Message):
    db = load_db()
    name = msg.text.strip()

    if name in db:
        bot.send_document(msg.chat.id, db[name], caption=name)
    else:
        bot.reply_to(msg, "🤔 Принт не найден. Попробуй другое слово.")

@server.route(f"/{API_TOKEN}", methods=['POST'])
def webhook():
    json_str = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "!", 200

@server.route("/")
def index():
    return "Бот работает ✅"

# ====================== Установка Webhook ======================

if
