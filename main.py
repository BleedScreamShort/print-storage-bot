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

# ===================== Обработка загрузки файлов =========================
@bot.message_handler(content_types=['document'])
def handle_doc(msg: Message):
    if msg.from_user.id != OWNER_ID:
        bot.reply_to(msg, "⛔ Только админ может загружать принты.")
        return

    file_name = msg.document.file_name
    file_id = msg.document.file_id

    db = load_db()
    if file_name in db:
        bot.send_message(msg.chat.id, f"⚠️ Такой принт уже есть: `{file_name}`. Заменить?", parse_mode="Markdown")
        bot.register_next_step_handler(msg, lambda m: confirm_replace(m, file_name, file_id))
    else:
        db[file_name] = file_id
        save_db(db)
        bot.send_message(msg.chat.id, f"✅ Добавлен новый принт: `{file_name}`", parse_mode="Markdown")

def confirm_replace(msg, file_name, new_file_id):
    text = msg.text.lower()
    if text in ["да", "заменить", "yes"]:
        db = load_db()
        db[file_name] = new_file_id
        save_db(db)
        bot.send_message(msg.chat.id, f"♻️ Принт `{file_name}` заменён.", parse_mode="Markdown")
    else:
        bot.send_message(msg.chat.id, "❌ Замена отменена.")

# ===================== Поиск по названию =========================
@bot.message_handler(func=lambda msg: True)
def search_print(msg: Message):
    query = msg.text.lower().replace(".png", "").replace("_б", "")
    db = load_db()

    matches = [name for name in db if query in name.lower()]
    if not matches:
        bot.send_message(msg.chat.id, "😕 Принт не найден. Попробуй другое слово.")
        return

    for name in matches:
        bot.send_document(msg.chat.id, db[name], caption=name)

# ===================== Flask Webhook =========================
@server.route(f"/{API_TOKEN}", methods=['POST'])
def webhook():
    json_str = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "!", 200

@server.route("/")
def index():
    return "Бот работает ✅"

# ===================== Webhook init =========================
if __name__ == "__main__":
    webhook_url = "https://print-storage-bot.onrender.com/" + API_TOKEN
    bot.remove_webhook()
    bot.set_webhook(url=webhook_url)
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
