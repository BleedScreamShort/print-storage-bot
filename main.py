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

# Создание базы данных, если она отсутствует
if not os.path.exists(DB_PATH):
    with open(DB_PATH, 'w', encoding='utf-8') as f:
        json.dump({}, f, ensure_ascii=False)

# Загрузка базы

def load_db():
    with open(DB_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

# Сохранение базы

def save_db(data):
    with open(DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# Нормализация текста

def normalize(text):
    return text.lower().replace(" ", "").replace("_", "")

# === Обработка документов (отправка принтов) ===
@bot.message_handler(content_types=['document'])
def handle_doc(msg: Message):
    if msg.from_user.id != OWNER_ID:
        return

    file_name = msg.document.file_name
    file_id = msg.document.file_id
    norm_name = normalize(file_name)

    db = load_db()
    db[norm_name] = {'name': file_name, 'file_id': file_id}
    save_db(db)

    bot.reply_to(msg, f"✅ Получено:\n📄 {file_name}\n🆔 {file_id}")

# === Поиск принта ===
@bot.message_handler(func=lambda msg: True, content_types=['text'])
def handle_search(msg: Message):
    if msg.text.startswith('/'):
        return  # игнорируем команды

    db = load_db()
    query = normalize(msg.text)
    result = db.get(query)

    if result:
        bot.send_document(msg.chat.id, result['file_id'], caption=result['name'])
    else:
        bot.reply_to(msg, "🤔 Принт не найден. Попробуй другое слово.")

# === Корневая страница ===
@server.route("/")
def index():
    return "Бот работает ✅"

# === Вебхук и запуск ===
if __name__ == '__main__':
    webhook_url = f"https://print-storage-bot.onrender.com/{API_TOKEN}"

    bot.remove_webhook()
    bot.set_webhook(url=webhook_url)

    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
