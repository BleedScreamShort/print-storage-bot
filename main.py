import os
import json
from flask import Flask, request
import telebot
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
        return

    file_info = bot.get_file(msg.document.file_id)
    file = bot.download_file(file_info.file_path)
    db = load_db()
    db[msg.document.file_name] = msg.document.file_id
    save_db(db)
    bot.reply_to(msg, f"✅ Получено:\n📄 {msg.document.file_name}\n🆔 `{msg.document.file_id}`", parse_mode="Markdown")

@bot.message_handler(func=lambda message: True, content_types=['text'])
def search_file(msg: Message):
    db = load_db()
    name = msg.text.strip()
    matches = {k: v for k, v in db.items() if name.lower() in k.lower()}
    if not matches:
        bot.send_message(msg.chat.id, "🤔 Принт не найден. Попробуй другое слово.")
    else:
        for filename, file_id in matches.items():
            bot.send_document(msg.chat.id, file_id, caption=filename)

@server.route(f"/{API_TOKEN}", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.get_data().decode("utf-8"))
    bot.process_new_updates([update])
    return "!", 200

@server.route("/", methods=["GET"])
def index():
    return "Бот работает ✅"

if __name__ == "__main__":
    webhook_url = f"https://print-storage-bot.onrender.com/{API_TOKEN}"
    bot.remove_webhook()
    bot.set_webhook(url=webhook_url)
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
