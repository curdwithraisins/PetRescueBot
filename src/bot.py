#!/usr/bin/env python3

import os
import time
import telegram

from telegram.ext import Updater, CommandHandler
from utils import get_env
from scapper import scrap

def start(update, context):
    chat_id = update.message.chat_id
    context.bot.sendMessage(chat_id, text="test", parse_mode=telegram.ParseMode.MARKDOWN)

def main():
    token = get_env("TOKEN")
    updater = Updater(token, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    updater.start_polling()

    while True:
        medias = scrap()
        print(medias[3])
        time.sleep(10)

main()