from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters, ContextTypes, \
    CallbackQueryHandler



async def BasicHandler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    user_input = user_input.lower()


    if user_input == "ruusu":
        await update.message.reply_text("powi.fi/ruusu/")

    elif user_input == "shotgun":
        await update.message.reply_text("@shotguntapahtuma")

