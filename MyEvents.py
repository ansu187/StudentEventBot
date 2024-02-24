import Event, EventDatabase, User, UserDatabase, Tags, Button
from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters, ContextTypes
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from datetime import datetime, timedelta
import asyncio

import Filepaths

CHOICE = 1


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    event_list = EventDatabase.get_events_by_creator(update)
    context.user_data['event_list'] = event_list
    await event_to_edit_keyboard(update,context,event_list)

    return CHOICE





async def choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    event_list = context.user_data['event_list']
    text = update.message.text.lower()

    for event in event_list:
        event_name = event.name.lower()
        if event_name == text:
            context.user_data['event'] = event

    event = context.user_data['event']

    keyboard = [
        [
            InlineKeyboardButton(Button.translate_string("Show likes", update),
                                 callback_data=f"{event.id};{Button.SHOW_LIKES}"),
            InlineKeyboardButton(Button.translate_string("Edit event", update),
                                 callback_data=f"{event.id};{Button.EDIT_EVENT}")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(f"{EventDatabase.get_head(event, UserDatabase.get_user_lang_code(update))}", reply_markup=reply_markup)







async def event_to_edit_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE, event_list):
    reply_keyboard = []

    for event in event_list:
        button = [f"{event.name}"]
        reply_keyboard.append(button)

    reply_keyboard.append(["/cancel"])

    await update.message.reply_text(
        f"what event do you want to check?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Choose an event?"
        ),
    )

    ReplyKeyboardRemove()
    return






