#!/usr/bin/env python3

import os
import time
import telegram

from redis_client import redis_client
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, ConversationHandler, CallbackQueryHandler, MessageHandler, Filters
from utils import get_env
from scapper import scrap

CITY, KIND, GENDER, DESCRIPTION, PHOTO = range(5)

def start(update, context):
    keyboard = [[InlineKeyboardButton("Киев", callback_data='Kiev'),
                 InlineKeyboardButton("Харьков", callback_data='Kharkiv'),
                 InlineKeyboardButton("Днепр", callback_data='Dnipro'),
                 InlineKeyboardButton("Львов", callback_data='Lviv'),
                 InlineKeyboardButton("Одесса", callback_data='Odessa')],
                [InlineKeyboardButton("Все", callback_data='All')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Выберите город:', reply_markup=reply_markup)

def cancel(update, context):
    update.message.reply_text('Ждем еще!', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END    

def adopt(update, context):
    reply_keyboard = [['Киев', 'Харьков', 'Днепр', 'Одессы', 'Львов', 'Везде']]
    update.message.reply_text("Хотите найти кому-то дом? Чудесно! " 
        "Давайте постараемся отыскать самых лучших хозяев вместе! Сначала расскажите, в каком городе будем искать.\n\n"
        "Если вы ошиблись, вы всегда можете отменить все, отправив слово /cancel.",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return CITY

def city(update, context):
    reply_keyboard = [['Собаку', 'Кота', 'Другое']]
    update.message.reply_text("Отлично! А теперь о любимце! Кого будем отдавать?", 
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return KIND

def kind(update, context):
    reply_keyboard = [['Мальчик', 'Девочка', 'Не понятно(']]
    update.message.reply_text("Отлично! А теперь о любимце! Кого будем отдавать?", 
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return GENDER

def gender(update, context):
    update.message.reply_text("Добавим немного информации о пушистике (или не очень), "
    "чтобы новые родители лучше узнали его. Можно милую историю появления или спасения :3")
    return DESCRIPTION

def description(update, context):
    update.message.reply_text("И пару фото, чтобы было лучше понятней, как выглядит ваше чудо)")
    return PHOTO

def photo(update, context):
    photo_file = update.message.photo[-1].get_file()
    print(photo_file['file_path'])
    update.message.reply_text('Класс! Сейчас запостим и начнется поиск родителей! Спасибо <3')

    return ConversationHandler.END

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
            for user in users_city:
                context.bot.sendMessage(user, text=post.link, parse_mode=telegram.ParseMode.HTML)     

def main():
    token = get_env("TOKEN")
    updater = Updater(token, use_context=True)
    dispatcher = updater.dispatcher
    
    dispatcher.add_handler(CallbackQueryHandler(select))
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(ConversationHandler(
        entry_points=[CommandHandler('adopt', adopt)],
        states={
            CITY: [MessageHandler(Filters.regex('^(Киев|Харьков|Днепр|Одессы|Львов|Везде)$'), city)],
            KIND: [MessageHandler(Filters.regex('^(Собаку|Кота|Другое)$'), kind)],
            GENDER: [MessageHandler(Filters.regex('^(Мальчик|Девочка)$'), gender)],
            DESCRIPTION: [MessageHandler(Filters.text, description)],
            PHOTO: [MessageHandler(Filters.photo, photo)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    ))

    updater.job_queue.run_repeating(broadcast, 300, 0)

    updater.start_polling()

main()