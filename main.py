import telebot
import json
import os
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

# === /start ===
@bot.message_handler(commands=['start'])
def handle_start(msg: Message):
    bot.reply_to(msg, "👋 Привет! Отправь название принта, и я поищу его. А если ты админ — просто пришли файл, и я его сохраню.")

# === Получение документа от админа ===
@bot.message_handler(content_types=['document'])
def handle_doc(msg: Message):
    if msg.from_user.id != OWNER_ID:
        bot.reply_to(msg, "⛔ У тебя нет прав на загрузку.")
        return

    file_name = msg.document.file_name
    file_id = msg.document.file_id

    data = load_db()
    data[file_name] = file_id
    save_db(data)

    bot.reply_to(msg, f"✅ Получено:\n📄 <b>{file_name}</b>\n🆔 <code>{file_id}</code>", parse_mode="HTML")

# === Поиск по названию ===
@bot.message_handler(content_types=['text'])
def handle_search(msg: Message):
    name = msg.text.strip()
    data = load_db()

    found = [(k, v) for k, v in data.items() if name.lower() in k.lower()]
    if not found:
        bot.reply_to(msg, "🤔 Принт не найден. Попробуй другое слово.")
        return

    for file_name, file_id in found[:10]:  # максимум 10
        bot.send_document(msg.chat.id, file_id, caption=file_name)

# === Flask Webhook ===
@server.route(f"/{API_TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "!", 200

@server.route("/")
def index():
    return "Бот работает ✅"

# === Запуск ===
if __name__ == "__main__":
    webhook_url = f"https://print-storage-bot.onrender.com/{API_TOKEN}"
    bot.remove_webhook()
    bot.set_webhook(url=webhook_url)
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
