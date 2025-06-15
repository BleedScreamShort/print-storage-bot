from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

TOKEN = '7237914704:AAGCgfYcBvNurGqC4Q1ZjFYdNZLbZdVKZ_I'
bot = TeleBot(TOKEN)

# Категории
categories = {
    "🏋️‍♂️ Спортзал": "Принты на тему спортзала 💪",
    "👨‍💼 Офис": "Принты для офисной жизни 💼",
    "🍉 Лето": "Шашлык, пиво, жара ☀️",
    "🧔‍♂️ Барбершоп": "Мужской стиль ✂️",
    "💅 Красота": "Маникюр, реснички ✨"
}

# Принты: ключ — имя без пробелов, значение — file_id
prints = {
    "два_мнения_б": "BQACAgIAAxkBAAMHaE7Xa9UScYXSD0nOWhux-86yRXUAAo9wAAIkFnBKnhwtnl-w-jI2BA",
    "настроение_б": "BQACAgIAAxkBAAMIaE7Xa8cF6g2WlJxOXK9QcyMhSR0AApBwAAIkFnBKRggF7HLGzp42BA"
}

# /start
@bot.message_handler(commands=['start'])
def start_handler(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for category in categories:
        markup.add(KeyboardButton(category))
    bot.send_message(message.chat.id, "Привет! Выбери категорию принтов:", reply_markup=markup)

# Ответ по категориям
@bot.message_handler(func=lambda msg: msg.text in categories)
def category_handler(message):
    bot.send_message(message.chat.id, categories[message.text])

# Поиск по названию
@bot.message_handler(func=lambda msg: True)
def search_handler(message):
    query = message.text.lower().replace(" ", "_")
    for name, file_id in prints.items():
        if query in name:
            bot.send_photo(message.chat.id, file_id, caption=f"🔎 Найдено: {name}")
            return
    bot.send_message(message.chat.id, "😕 Принт не найден. Попробуй другое слово.")

bot.polling()
