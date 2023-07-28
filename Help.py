from telegram import Update
from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters, ContextTypes
import UserDatabase
import User


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if UserDatabase.get_user_type(update) == 1:
        if UserDatabase.get_user_lang(update) == "fi":
            await update.message.reply_text("Hei! Autan löytämään sinua kiinnostavat skinnarilalaiset opiskelijatapahtumat helposti!\n\n"
                                            "Lähetän sinulle tapahtumia, aina kun niitä julkaistaan. Voit valita mitä tapahtumia sinulle lähetän komennolla /tags."
                                            "Voit muuttaa näitä tägejä aina kun haluat!\n\n"
                                            "Kirjottamalla minulle /list lähetän sinulle kaikki tulevat tapahtumat aikajärjestyksessä!\n\n"
                                            "Voit myös kirjoittaa /list-komennon perään ohjeita, jonka mukaan listaan tapahtumat\n\n"
                                            "Kirjoittamalla /list ja jonkun numeron, lähetän sinulle yhtä monta tapahtumaa aikajärjestyksessä\n\n"
                                            "Kirjoittamalla /list next week, lähetän sinulle seuraavan viikon tapahtumat\n\n"
                                            "kirjoittamalla /list #, avaan sinulle näppäimistön, josta voit valita tägin, ja lähetän sinulle sen tägin mukaiset tapahtumat aikajärjestyksessä!\n\n"
                                            "")
        else:
            await update.message.reply_text("This bot helps you to find events")

    else:
        await update.message.reply_text("Pitäs osata käyttää jo ilman apua!")
