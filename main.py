import os
import telebot
from flask import Flask, request

API_TOKEN = os.getenv("API_TOKEN")
OWNER_ID = os.getenv("OWNER_ID")

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# Убедимся, что папка prints существует
if not os.path.exists("prints"):
    os.makedirs("prints")

@app.route(f"/{API_TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "!", 200

@app.route("/")
def index():
    return "Бот работает 🛡", 200

@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_message(message.chat.id, "📫 Бот готов. Просто отправь название принта.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text.strip()
    print(f"\n[LOG] Сообщение: {text}")
    print("[LOG] Файлы в prints/:", os.listdir("prints"))

    found = False
    for filename in os.listdir("prints"):
        if text.lower() in filename.lower():
            path = os.path.join("prints", filename)
            with open(path, "rb") as f:
                bot.send_document(message.chat.id, f, caption=filename)
            found = True
            break

    if not found:
        bot.send_message(message.chat.id, "🤔 Принт не найден. Попробуй другое слово.")

if __name__ == "__main__":
    webhook_url = f"https://print-storage-bot.onrender.com/{API_TOKEN}"
    bot.remove_webhook()
    bot.set_webhook(url=webhook_url)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
