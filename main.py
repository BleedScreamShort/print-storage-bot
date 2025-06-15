from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

TOKEN = 'ТВОЙ_ТОКЕН_ОТСЮДА_ПОДСТАВЬ'  # вставь свой токен от BotFather
bot = TeleBot(TOKEN)

categories = {
    "🏋 Спортзал": "Принты на тему спортзала 💪",
    "🧑‍💼 Офис": "Принты для офисной жизни ☕",
    "🏕 Лето": "Шашлыки, пиво, жара 🌞",
    "💈 Барбершоп": "Мужской стиль 💈",
    "💅 Красота": "Маникюр, реснички ✨"
}

@bot.message_handler(commands=['start'])
def start_handler(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for category in categories:
        markup.add(KeyboardButton(category))
    bot.send_message(message.chat.id, "Привет! Выбери категорию принтов:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in categories)
def category_handler(message):
    bot.send_message(message.chat.id, categories[message.text])

@bot.message_handler(content_types=['document'])
def catch_file_id(message):
    file_id = message.document.file_id
    file_name = message.document.file_name
    bot.send_message(message.chat.id, f"✅ Получено:\n📄 {file_name}\n🆔 {file_id}")

bot.polling()
