import os
import json
import telebot
from flask import Flask, request

API_TOKEN = os.getenv("API_TOKEN")
OWNER_ID = os.getenv("OWNER_ID")

bot = telebot.TeleBot(API_TOKEN)
server = Flask(__name__)

# === Загрузка базы принтов ===
if os.path.exists("storage.json"):
    with open("storage.json", "r", encoding="utf-8") as f:
        database = json.load(f)
else:
    database = []

# === Обработка команды /start ===
@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.send_message(message.chat.id, "\U0001F4E3 Бот готов. Просто отправь название принта.")

# === Обработка обычных сообщений (поиск принтов) ===
@bot.message_handler(func=lambda m: True)
def handle_query(message):
    query = message.text.lower().replace(" ", "").replace("_", "")
    matches = [item for item in database if query in item["name"].lower().replace(" ", "").replace("_", "")]

    if matches:
        for match in matches:
            bot.send_document(message.chat.id, match["file_id"], caption=match["name"])
    else:
        bot.send_message(message.chat.id, "🤔 Принт не найден. Попробуй другое слово.")

# === Webhook обработчик ===
@server.route(f"/{API_TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "!", 200

@server.route("/")
def index():
    return "Бот работает ✅"

# === Запуск Webhook-сервера ===
if __name__ == "__main__":
    webhook_url = f"https://print-storage-bot.onrender.com/{API_TOKEN}"
    bot.remove_webhook()
    bot.set_webhook(url=webhook_url)
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
