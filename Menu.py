import logging
from datetime import datetime

from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters, ContextTypes, \
    CallbackQueryHandler

import Accept
import Event, UserDatabase, EventDatabase
import Tags



async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_lang = UserDatabase.get_user_lang(update)
    if user_lang == "fi":
        lang_code = 0
        reply_keyboard = [["Listaa tapahtumat", "Change language"], ["Anna palautetta", "Vaihda tagit"]]
    else:
        lang_code = 1
        reply_keyboard = [["List events", "Vaihda kieli"], ["Give feedback", "Change tags"]]

    prompts = [["Mitä haluat tehdä?"],["What do you want to do?"]]




    await update.message.reply_text(
        f"{prompts[lang_code][0]}",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Menu"
        ),
    )

    ReplyKeyboardRemove()

    return