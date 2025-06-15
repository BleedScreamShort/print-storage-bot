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

def normalize(text):
    return text.lower().replace(" ", "").replace("_", "")

# ================= Обработка загрузки файлов =====================
@bot.message_handler(content_types=['document'])
def handle_doc(msg: Message):
    if msg.from_user.id != OWNER_ID:
        return

    file_name = msg.document.file_name
    file_id = msg.document.file_id

    data = load_db()
    data[file_name] = file_id
    save_db(data)

    bot.reply_to(msg, f"✅ Получено:\n📄 {file_name}\n🆔 `{file_id}`", parse_mode="Markdown")

# ================= Поиск по названию =====================
@bot.message_handler(content_types=['text'])
def handle_text(msg: Message):
    text = normalize(msg.text)
    data = load_db()

    for name, file_id in data.items():
        if text in normalize(name):
            bot.send_document(msg.chat.id, file_id, caption=name)
            return

    bot.reply_to(msg, "🤔 Принт не найден. Попробуй другое слово.")

# ================= Webhook =====================
@server.route(f"/{API_TOKEN}", methods=['POST'])
def webhook():
    json_str = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "!", 200

@server.route("/")
def index():
    return "Бот работает ✅"

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"https://print-storage-bot.onrender.com/{API_TOKEN}")
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
