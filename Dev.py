from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters, ContextTypes, \
    CallbackQueryHandler
import UserDatabase, EventDatabase, Event
import json


async def dev(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        arguments = context.args
        arguments = " ".join(arguments)
        arguments = arguments.lower()
    except TypeError:
        arguments = ""


    try:
        with open('tags.json', 'r') as file:
            data = json.load(file)
            tags_list = data.get('tags', [])

            # Append the attribute_value to the last list in chunks of 3 strings
            last_list = tags_list[-1] if tags_list else []
            if len(last_list) < 3:
                last_list.append(arguments)
            else:
                tags_list.append([arguments])

            data['tags'] = tags_list

        with open('tags.json', 'w') as file:
            json.dump(data, file, indent=2)

        await update.message.reply_text(f"Attribute '{arguments}' added to tags.json.")

    except (FileNotFoundError, json.JSONDecodeError):
        await update.message.reply_text("Error: Unable to modify tags.json.")



