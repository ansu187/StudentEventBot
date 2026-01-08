from telegram.ext import ContextTypes, ConversationHandler
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove


import MessageSender
import User

import UserDatabase


DATA_COLLECTION, LANG = range(2)


async def lang_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
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



    #Gets user data
    user_list = UserDatabase.user_reader()





    #Handles the new user


    user_id = update.message.from_user.id

    #Sets the basic values
    new_user = User.User(user_id, update.message.from_user.username, [], 1)

    #Checks if the user is allready in the database
    context.user_data['old_user'] = UserDatabase.is_user(update)

    if not context.user_data['old_user']:
        lang = update.message.from_user.language_code
        if lang == "fi":
            await update.message.reply_text(
                "Tervetuloa käyttämään Skinnarila Events Bottia!\n\n"
                "TÄMÄ VERSIO ON edelleen BETA, JA ON ERITTÄIN TODENNÄKÖISTÄ ETTEI MIKÄÄN TOIMI.\n\n"
                "Tämän botin on kirjoittanut kylteri apunaan ChatGPT 3.5, kelaa miten pitkä aika siitä on!\n\n\n"
                "Onko ok, jos tallennamme Telegram ID:n, Telegram käyttäjänimen ja valitsemasi kielen. "
                "Nämä tiedot eivät ole tallennettu tietoturvallisesti. Onko tämä ok, jos ei, botti ei toimi :(")

            reply_keyboard = [["Kyllä", "Ei"]]

            await update.message.reply_text(
                f"Käykö jos tallennamme tietosi?",
                reply_markup=ReplyKeyboardMarkup(
                    reply_keyboard, one_time_keyboard=True, input_field_placeholder="Valintasi:"
                ),
            )
            ReplyKeyboardRemove()
            context.user_data['user'] = new_user
            return DATA_COLLECTION

        else:
            await update.message.reply_text(
                "Welcome to use the Skinnarila Student Events bot!\n\n"
                "THIS VERSION IS CURRENTLY still IN BETA AND THERE IS HIGH CHANGE OF NOTHING WORKING\n\n"
                "Bot is written by kylteri with ChatGPT 3.5, think how long time ago that was!\n\n\n"
                "Is it okay if we save your Telegram ID, Telegram username and the language that you choose. "
                "This information is not saved securely. Is this okay for you, if not, the bot won't work :(")

            reply_keyboard = [["Yes", "No"]]

            await update.message.reply_text(
                f"Is it okay that we save?",
                reply_markup=ReplyKeyboardMarkup(
                    reply_keyboard, one_time_keyboard=True, input_field_placeholder="Your choice:"
                ),
            )
            ReplyKeyboardRemove()
            context.user_data['user'] = new_user
            return DATA_COLLECTION



    await lang_keyboard(update, context)
    return LANG


async def data_collection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    user_text = user_text.lower()

    if user_text == "kyllä" or user_text == "yes":

        await lang_keyboard(update,context)
        return LANG

    else:
        await update.message.reply_text("Nothing saved, the bot will not work.")
        return ConversationHandler.END


async def lang(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text_in = update.message.text.lower()
    try:
        new_user = context.user_data['user']
    except KeyError:
        pass
    user_list = UserDatabase.user_reader()

    if context.user_data['old_user']:
        user_id = update.message.from_user.id
        for user in user_list:
            if user_id == user.id:
                if text_in == "finnish":
                    user.user_lang = "fi"
                elif text_in == "english":
                    user.user_lang = "en"
                UserDatabase.user_writer(user_list)

        if UserDatabase.get_user_lang(update) == "en":
            await update.message.reply_text("Your language has been changed!")
        elif UserDatabase.get_user_lang(update) == "fi":
            await update.message.reply_text("Kieli vaihdettu!")
        return ConversationHandler.END

    if text_in == "finnish":
        new_user.user_lang = "fi"

    elif text_in == "english":
        new_user.user_lang = "en"


    user_list.append(new_user)

    UserDatabase.user_writer(user_list)


    await update.message.reply_text("Your account is now saved!\nHere are the upcoming events!")

    await MessageSender.send_all_events(update, context)

    return ConversationHandler.END

