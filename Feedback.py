from telegram import Update
from telegram.ext import ConversationHandler, ContextTypes
import UserDatabase
import Filepaths

FEEDBACK = 1

async def feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if UserDatabase.get_user_lang(update) == "fi":
        await update.message.reply_text("Tervetuloa lähettämään palautetta!"
                                        "Tallennan palautteen yhteyteen käyttäjänimesi, "
                                        "että ylläpitäjät voivat palata sinulle asian tiimoilta!"
                                        "\n\nKirjoita palaute tähän alle:"
                                        )

    else:
        await update.message.reply_text("Welcome to leave some feedback!"
                                  "I'll save your username with the feedback in order to return to you regarding it if neccessary!"
                                  "\n\nWrite the feedback down here:")
    print("Returning")
    return FEEDBACK



async def save_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        with open(Filepaths.feedback_file, "a") as f:
            f.write(f"{update.message.from_user.username}: {update.message.text}\n")
            if UserDatabase.get_user_lang_code(update) == 0:
                await update.message.reply_text("Palaute vastaanotettu!")
            else:
                await update.message.reply_text("Feedback received!")

    except FileNotFoundError:
        try:
            with open(Filepaths.feedback_file, "w") as f:
                f.write(f"{update.message.from_user.username}: {update.message.text}\n")
                print("File created!")
        except FileNotFoundError:
            print("Something went wrong!")

    return ConversationHandler.END