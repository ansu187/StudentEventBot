

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes

import UserDatabase




async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_lang = UserDatabase.get_user_lang(update)
    if user_lang == "fi":
        lang_code = 0
        reply_keyboard = [["Listaa tapahtumat"], ["Anna palautetta", "Change language"]]
        if UserDatabase.get_user_type(update) >= 2:
            reply_keyboard.append(["Luo tapahtuma", "Muokkaa tapahtumaa"])
        if UserDatabase.get_user_type(update) == 3:
            reply_keyboard.append(["Hyväksy tapahtumia"])
        if UserDatabase.get_user_type(update) >= 4:
            reply_keyboard.append(["Hyväksy tapahtumia", "Salainen menu"])

    else:
        lang_code = 1
        reply_keyboard = [["List events", "Change tags"], ["Give feedback", "Vaihda kieli"]]
        if UserDatabase.get_user_type(update) >= 2:
            reply_keyboard.append(["Create event", "Edit event"])
        if UserDatabase.get_user_type(update) == 3:
            reply_keyboard.append(["Accept events"])
        if UserDatabase.get_user_type(update) >= 4:
            reply_keyboard.append(["Accept events", "Secret menu"])

    prompts = [["Mitä haluat tehdä?"],["What do you want to do?"]]




    await update.message.reply_text(
        f"{prompts[lang_code][0]}",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Menu"
        ),
    )

    ReplyKeyboardRemove()

    return