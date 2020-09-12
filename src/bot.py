#!/usr/bin/env python3

import os
import time
import telegram

from redis_client import redis_client
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, InputMediaPhoto, KeyboardButton
from telegram.ext import Updater, CommandHandler, ConversationHandler, CallbackQueryHandler, MessageHandler, Filters
from utils import get_env
from scapper import scrap

adoptions = {}
CITY, KIND, GENDER, NAME, DESCRIPTION, PHOTO, CONTACT = range(7)

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
    reply_markup = ReplyKeyboardMarkup([[KeyboardButton(text="Найти хозяев")]])
    query.message.reply_text("Спасибо! Теперь вы будете получать уведомления по выбранному городу!", reply_markup=reply_markup)  

def adopt(update, context):
    adoptions[update.message.from_user] = {}
    reply_keyboard = [['Киев', 'Харьков', 'Днепр', 'Одессы', 'Львов', 'Везде'], ['Отменить']]
    update.message.reply_text("Хотите найти кому-то дом? Чудесно! " 
        "Давайте постараемся отыскать самых лучших хозяев вместе! Сначала расскажите, в каком городе будем искать.\n\n"
        "Если вы ошиблись, можете отменить.",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return CITY

def city(update, context):
    adoptions[update.message.from_user]['city'] = update.message.text
    reply_keyboard = [['Собака', 'Кот', 'Другое'], ['Отменить']]
    update.message.reply_text("Отлично! А теперь о любимце! Кого будем отдавать?", 
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return KIND

def kind(update, context):
    adoptions[update.message.from_user]['kind'] = update.message.text
    reply_keyboard = [['Мальчик', 'Девочка', 'Не понятно('], ['Отменить']]
    update.message.reply_text("А какой пол?", 
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return GENDER

def gender(update, context):
    adoptions[update.message.from_user]['gender'] = update.message.text
    reply_keyboard = [['Отменить']]
    update.message.reply_text("Уже придумали имя? Можете поделиться им тоже!", 
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return NAME

def name(update, context):
    adoptions[update.message.from_user]['name'] = update.message.text
    reply_keyboard = [['Отменить']]
    update.message.reply_text("Как с вами связаться? Вы можете добавить номер телефона, "
        "аккаунт в инстаграме, телеграме или любой другой способ!",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return CONTACT

def contact(update, context):
    adoptions[update.message.from_user]['contact'] = update.message.text
    reply_keyboard = [['Отменить']]
    update.message.reply_text("Добавим немного информации о пушистике (или не очень), "
    "чтобы новые родители лучше узнали его. Можно милую историю появления или спасения :3",
    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return DESCRIPTION     

def description(update, context):
    reply_keyboard = [['Отменить']]
    adoptions[update.message.from_user]['description'] = update.message.text
    update.message.reply_text("И пару фото, чтобы было лучше понятней, как выглядит ваше чудо)",
    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return PHOTO

def photo(update, context):
    photo_file = update.message.photo[-1]
    print(photo_file)
    if not 'photo' in adoptions[update.message.from_user]:
        adoptions[update.message.from_user]['photo'] = []
    adoptions[update.message.from_user]['photo'].append(photo_file['file_id'])

    if (len(adoptions[update.message.from_user]['photo']) < 5):
        reply_keyboard = [['Закончить']]
        update.message.reply_text('Еще фото? Если хватит, то можем на этом закончить!',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))        
        return PHOTO
    
    skip_photo(update, context)

def skip_photo(update, context):
    media_group = []
    for file_id in adoptions[update.message.from_user]['photo']:
        media_group.append(InputMediaPhoto(media=file_id))

    update.message.reply_text('Класс! Сейчас запостим и начнется поиск родителей! Спасибо <3')
    update.message.reply_text(text=parse(adoptions[update.message.from_user]), parse_mode=telegram.ParseMode.MARKDOWN)
    context.bot.send_media_group(update.message.chat.id, media=media_group)

    return ConversationHandler.END

def cancel(update, context):
    del adoptions[update.message.from_user]
    reply_markup = ReplyKeyboardMarkup([[KeyboardButton(text="Найти хозяев")]])
    update.message.reply_text('Ждем еще!', reply_markup=reply_markup)
    return ConversationHandler.END    

def parse(data):
    content = ("*Новый питомец ищет дом!*"
        "\n\U0001F4CD {city}\n\U0001F43E {kind}\n\U0001F536 {gender}\n\U0001F4AC {name}\n\U0001F4DE {contact}\n\n{desc}\n\n"
            ).format(city=data['city'], kind=data['kind'], gender=data['gender'], name=data['name'], contact=data['contact'], desc=data['description'])
    return content

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
        entry_points=[MessageHandler(Filters.regex("Найти"), adopt)],
        states={
            CITY: [MessageHandler(Filters.regex('^(Киев|Харьков|Днепр|Одессы|Львов|Везде)$'), city)],
            KIND: [MessageHandler(Filters.regex('^(Собака|Кот|Другое)$'), kind)],
            GENDER: [MessageHandler(Filters.regex('^(Мальчик|Девочка)$'), gender)],
            NAME: [MessageHandler(Filters.text, name)],
            CONTACT: [MessageHandler(Filters.text, contact)],
            DESCRIPTION: [MessageHandler(Filters.text, description)],
            PHOTO: [MessageHandler(Filters.photo, photo), MessageHandler(Filters.regex('Закончить'), skip_photo)]
        },
        fallbacks=[MessageHandler(Filters.regex('Отменить'), cancel)]
    ))

    # updater.job_queue.run_repeating(broadcast, 300, 0)

    updater.start_polling()

main()