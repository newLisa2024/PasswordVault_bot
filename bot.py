import telebot
from telebot.types import ReplyKeyboardMarkup, WebAppInfo
from dotenv import load_dotenv
import os

# Загрузка переменных окружения
load_dotenv()
bot_token = os.getenv('TOKEN')

# Инициализация бота
bot = telebot.TeleBot(bot_token)


# Команда для открытия Web App
@bot.message_handler(commands=['start'])
def start(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    webAppLink = WebAppInfo("http://127.0.0.1:5000/")  # Локальный сервер Flask
    markup.add(telebot.types.KeyboardButton(text="Открыть Web App", web_app=webAppLink))

    bot.send_message(message.chat.id, "Нажми кнопку ниже, чтобы открыть Web App.", reply_markup=markup)


# Запуск бота
bot.polling()


