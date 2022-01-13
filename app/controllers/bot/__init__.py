import telebot
from config import BaseConfig as conf
from app.controllers import get_status


class Bot:
    def __init__(self) -> None:
        self.bot = telebot.TeleBot(conf.BOT_API_TOKEN)
        self.add_handlers()

    def add_handlers(self):
        @self.bot.message_handler(commands=["status"])
        def status(message):
            self.bot.reply_to(message, get_status())

        @self.bot.message_handler(content_types=["text"])
        def reply(message):
            self.bot.reply_to(message, "For getting status of update type: '/status'")

    def start(self):
        self.bot.polling()
