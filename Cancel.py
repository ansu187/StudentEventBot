from telegram.ext import Application, CommandHandler, ConversationHandler, ContextTypes
from telegram import Update

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    print("User %s canceled the conversation.", user.first_name)



    return ConversationHandler.END