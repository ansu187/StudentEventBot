from telegram.ext import CommandHandler, ContextTypes, ConversationHandler
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
import json

import List
import User
import os
import UserDatabase


LANG = 0


async def keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [["finnish", "english"]]

    await update.message.reply_text(
        f"What language do you want to use?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Language:"
        ),
    )

    ReplyKeyboardRemove()
    return


async def tags(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #Handle the tags :D
    user_list = context.user_data["user_list"]
    new_user = context.user_data["new_user"]
    user_list.append(new_user)

    UserDatabase.user_writer(user_list)


    await update.message.reply_text("Your account is now saved!")

    return ConversationHandler.END





async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    #Handles the argument
    arguments = context.args
    arguments = " ".join(arguments)
    arguments = arguments.lower()


    #Gets user data
    user_list = UserDatabase.user_reader()


    #sets the user type to organizer
    if arguments == "organizer":
        await update.message.reply_text("Welcome to organize events! You'll now have an access for creating events")


        user_id = update.message.from_user.id
        for user in user_list:
            if user_id == user.id:
                user.user_type = 2

        UserDatabase.user_writer(user_list)

        return ConversationHandler.END



    #Handles the new user
    else:

        user_id = update.message.from_user.id

        #Sets the basic values
        user = User.User(user_id, update.message.from_user.username, ["#all"], 1)

        #Checks if the user is allready in the database
        context.user_data['old_user'] = False
        for user in user_list:
            if user.id == user_id:
                context.user_data['old_user'] = True

        if not context.user_data['old_user']:
            await update.message.reply_text(
                "Welcome to use the Skinnarila Student Events bot! This bot is going to save your Telegram ID, and will send you messages about the new events.")


        context.user_data['user'] = user


    await keyboard(update,context)
    return LANG










async def lang(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    input = update.message.text.lower()
    new_user = context.user_data['user']
    user_list = UserDatabase.user_reader()

    if context.user_data['old_user']:
        user_id = update.message.from_user.id
        for user in user_list:
            if user_id == user.id:
                if input == "finnish":
                    user.user_lang = "fi"
                elif input == "english":
                    user.user_lang = "en"
                UserDatabase.user_writer(user_list)

        if UserDatabase.get_user_lang(update) == "en":
            await update.message.reply_text("Your language has been changed!")
        elif UserDatabase.get_user_lang(update) == "fi":
            await update.message.reply_text("Kieli vaihdettu!")
        return ConversationHandler.END

    if input == "finnish":
        new_user.user_lang = "fi"

    elif input == "english":
        new_user.user_lang = "en"


    user_list.append(new_user)

    UserDatabase.user_writer(user_list)


    await update.message.reply_text("Your account is now saved!\nHere are the upcoming events!")
    await List.list(update, context)

    return ConversationHandler.END

