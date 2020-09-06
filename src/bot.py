#!/usr/bin/env python3
import os
import telegram

from telegram.ext import Updater, CommandHandler
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)
token = os.getenv("TOKEN")

def start(update, context):
    uid = update.message.chat_id
    context.bot.sendMessage(chat_id=update.message.chat_id, text="test",
                    parse_mode=telegram.ParseMode.MARKDOWN)

def main():
    updater = Updater(token, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    updater.start_polling()

main()