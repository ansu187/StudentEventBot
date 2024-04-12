import Event, EventDatabase, User, UserDatabase, Tags, MessageSender, EventLiker
from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters, ContextTypes
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from datetime import datetime, timedelta
import asyncio

import Start

ACTION_SELECTOR, USER_INFO, ADD_USERNAME, DELETE_USER, LANG = range(5)


commands = [[["Näytä käyttäjän tiedot", "Lisää käyttäjänimi", "Vaihda tagit"], ["Poista käyttäjä", "Change the language", "/cancel"]],
            [["Show account info", "Add username", "Change tags"], ["Delete account", "Vaihda kieli", "/cancel"]]]

async def menu_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE):

    reply_keyboard = commands[UserDatabase.get_user_lang_code(update)]

    await update.message.reply_text(
        f"What do you want to do",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Select event"
        ),
    )

    ReplyKeyboardRemove()

async def userinfo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await menu_keyboard(update, context)

    return ACTION_SELECTOR

async def action_selector(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_lang_code = UserDatabase.get_user_lang_code(update)
    user_prompt = update.message.text

    if not UserDatabase.is_user(update):
        await update.message.reply_text("User not found, something went wrong and the world will burn now!")
        return ConversationHandler.END

    if user_prompt == f"{commands[user_lang_code][0][0]}": #get user info
        await update.message.reply_text(f"{UserDatabase.get_user_info_text(update)}")
        return ConversationHandler.END

    elif user_prompt == f"{commands[user_lang_code][0][1]}": #change user name
        UserDatabase.update_username(update)
        return
    
    elif user_prompt == f"{commands[user_lang_code][0][2]}": #tags
        await Tags.tags(update, context)
        return Tags.EDIT

    elif user_prompt == f"{commands[user_lang_code][1][0]}": #delete account
        reply_keyboard = [["Yes", "No"]]

        await update.message.reply_text(
            f"Are you sure that you want to delete your account?",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True, input_field_placeholder=""
            ),
        )

        ReplyKeyboardRemove()
        return DELETE_USER

    elif user_prompt == f"{commands[user_lang_code][1][1]}": #change lang
        await Start.lang_keyboard(update, context)

        #needed in order to make the start lang function to work, hacky shit :D
        context.user_data["old_user"] = True
        return LANG


    else:
        await update.message.reply_text("Give me a correct input please!")
        await menu_keyboard(update,context)
        return ACTION_SELECTOR


async def change_languange(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await Start.lang(update, context)

    return ConversationHandler.END

async def delete_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_prompt = update.message.text
    user_prompt = user_prompt.lower()
    if user_prompt == "no":
        await update.message.reply_text("Phew, I already thought...")
        return ConversationHandler.END
    else:
        UserDatabase.delete_user(update.message.from_user.id)
        await update.message.reply_text("Your user is now deleted and I'll send you messages no more. If you want to return, "
                                        "just say me /start and I'll work again!")
        return ConversationHandler.END