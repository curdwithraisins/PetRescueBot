#!/usr/bin/env python3

import os
import time
import telegram

from redis_client import redis_client
from telegram.ext import Updater, CommandHandler
from utils import get_env
from scapper import scrap

def start(update, context):
    chat_id = update.message.chat_id
    redis_client.add_user({"id": chat_id, "pref": {"kind": "cat", "sex": "male"}})
    context.bot.sendMessage(chat_id, text="test", parse_mode=telegram.ParseMode.MARKDOWN)

def parse(media):
    return "<img src={m} />".format(m=media.image_standard_resolution_url)

def broadcast(context):
    data = scrap()
    print(data[6].image_high_resolution_url)
    for user in redis_client.get_users():
        context.bot.sendPhoto(user['id'], photo='{m}'.format(m=data[6].image_standard_resolution_url))     

def main():
    token = get_env("TOKEN")
    updater = Updater(token, use_context=True)
    dispatcher = updater.dispatcher
    
    dispatcher.add_handler(CommandHandler("start", start))

    updater.job_queue.run_repeating(broadcast, 10, 0)

    updater.start_polling()

main()