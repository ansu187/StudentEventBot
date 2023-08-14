import logging
from datetime import datetime

from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters, ContextTypes, \
    CallbackQueryHandler

import Accept
import Event, UserDatabase, EventDatabase
import Tags



async def Menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_lang = UserDatabase.get_user_lang(update)

    reply_keyboard = [["all"], ["#alcohol-free", "#sits", "#appro"], ["#bar", "#kellari"]]

    await update.message.reply_text(
        f"?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Event tags"
        ),
    )

    ReplyKeyboardRemove()