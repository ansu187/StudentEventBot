from telegram.ext import CommandHandler, ContextTypes, ConversationHandler
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
import json

import List
import User
import os
import UserDatabase



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

        return



    #Handles the new user
    else:
        await update.message.reply_text("Welcome to use the Skinnarila Student Events bot! This bot is going to save your Telegram ID, and will send you messages about the new events.")
        user_id = update.message.from_user.id

        #Sets the basic values
        new_user = User.User(user_id, update.message.from_user.username, ["#all"], 1, update.message.from_user.language_code)

        #Checks if the user is allready in the database
        found = False
        for user in user_list:
            if user.id == user_id:
                found = True
                break

        #If not, adds it to the list
        if not found:

            user_list.append(new_user)
            print(f"New user added {update.message.from_user.username}!")




        #Writes the userlist into the database
        UserDatabase.user_writer(user_list)

        #Sends confirmation message
        if found:
            await update.message.reply_text("You already have an account!")

        else:
            await update.message.reply_text("Your account is now saved!")
            await List.list(update, context)




