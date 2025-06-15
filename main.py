import os
import json
import telebot
from flask import Flask, request
from telebot.types import Message

API_TOKEN = os.environ.get("API_TOKEN")
OWNER_ID = int(os.environ.get("OWNER_ID"))

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

DB_PATH = "database.json"
if not os.path.exists(DB_PATH):
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump({}, f, ensure_ascii=False)

def load_db():
    with open(DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_db(data):
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# === Обработка документов ===
@bot.message_handler(content_types=['document'])
def handle_doc(msg: Message):
    if msg.from_user.id != OWNER_ID:
        bot.reply_to(msg, "⛔ Только владелец может добавлять принты")
        return

    doc = msg.document
    file_id = doc.file_id
    file_name = doc.file_name

    db = load_db()
    is_new = file_name not in db
    db[file_name] = file_id
    save_db(db)

    bot.reply_to(msg, f"{'✅ Получено:' if is_new else '♻️ Обновлено:'}\n📁 {file_name}\n🪪 `{file_id}`", parse_mode="Markdown")

# === Поиск по названию ===
@bot.message_handler(content_types=['text'])
def handle_text(msg: Message):
    db = load_db()
    name = msg.text.strip()

    if name in db:
        bot.send_document(msg.chat.id, db[name], caption=name)
    else:
        bot.reply_to(msg, "🤔 Принт не найден. Попробуй другое слово.")

# === Webhook ===
@app.route(f"/{API_TOKEN}", methods=['POST'])
def webhook():
    json_str = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "!", 200

@app.route("/")
def index():
    return "Бот работает ✅"

# === Запуск Flask ===
if __name__ == '__main__':
    webhook_url = f"https://print-storage-bot.onrender.com/{API_TOKEN}"
    bot.remove_webhook()
    bot.set_webhook(url=webhook_url)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
