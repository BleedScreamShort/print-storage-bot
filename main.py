import os
import telebot
from flask import Flask, request, jsonify

API_TOKEN = os.environ.get("API_TOKEN")
OWNER_ID = int(os.environ.get("OWNER_ID"))  # Telegram user ID (int)
bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# === Webhook route ===
@app.route(f"/{API_TOKEN}", methods=['POST'])
def webhook():
    json_str = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

# === Healthcheck ===
@app.route("/", methods=["GET"])
def index():
    return "🤖 Bot is running!", 200

# === Message handler ===
@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_message(message):
    if message.from_user.id != OWNER_ID:
        return  # Ignore messages from strangers

    text = message.text.strip()

    # /start команду обрабатываем отдельно
    if text.startswith("/start"):
        bot.send_message(message.chat.id, "👋 Бот готов. Просто отправь название принта.")
        return

    # Пытаемся найти файл
    found = False
    for filename in os.listdir("prints"):
        if filename.lower().startswith(text.lower()):
            path = os.path.join("prints", filename)
            bot.send_document(message.chat.id, open(path, "rb"), caption=filename)
            found = True
            break

    if not found:
        bot.send_message(message.chat.id, "🤔 Принт не найден. Попробуй другое слово.")

# === Webhook setup ===
if __name__ == "__main__":
    WEBHOOK_HOST = "https://print-storage-bot.onrender.com"
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_HOST}/{API_TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
