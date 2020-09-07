#!/usr/bin/env python3

import os
import time
import telegram

from redis_client import redis_client
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from utils import get_env
from scapper import scrap

def start(update, context):
    keyboard = [[InlineKeyboardButton("Киев", callback_data='Kiev'),
                 InlineKeyboardButton("Харьков", callback_data='Kharkiv'),
                 InlineKeyboardButton("Днепр", callback_data='Dnipro'),
                 InlineKeyboardButton("Львов", callback_data='Lviv'),
                 InlineKeyboardButton("Одесса", callback_data='Odessa')],
                [InlineKeyboardButton("Все", callback_data='All')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Выберите город:', reply_markup=reply_markup)

def select(update, context):
    query = update.callback_query
    query.answer()
    redis_client.add_user(query.data, query.message.chat.id)
    query.edit_message_text(text="Спасибо! Теперь вы будете получать уведомления по выбранному городу!")

def broadcast(context):
    cities = redis_client.get_cities()
    all_users = redis_client.get_users('All')
    for city in cities:
        users_city = redis_client.get_users(city)
        users_city.extend(all_users)
        posts = scrap(city)
        for post in posts:
            print(post)
            for user in users_city:
                context.bot.sendMessage(user, text=post.link, parse_mode=telegram.ParseMode.HTML)     

def main():
    token = get_env("TOKEN")
    updater = Updater(token, use_context=True)
    dispatcher = updater.dispatcher
    
    dispatcher.add_handler(CallbackQueryHandler(select))
    dispatcher.add_handler(CommandHandler("start", start))

    updater.job_queue.run_repeating(broadcast, 300, 0)

    updater.start_polling()

main()