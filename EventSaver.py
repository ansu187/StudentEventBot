"""
This file contains everything regarding the event saving and editing
Conversation handler works with return values, that point to the next step in the process.
They all are integer constants, going up from 0.
The same constant can be used to address the correct prompt for the user with: user_prompts[insert constant here].
All Event objects have that are stored to the event_backups.json have a stage variable,
which is used to store where they were in the creating of the event.
So if the user is editing the accessibility_fi, and it crashes or the user cancels or something,
the Event.stage = ACCESSIBILITY_EN, which is value of 12.
When the user returns, it will ask if they want to continue editing the event.
If yes, it will display the prompt with user_prompts[Event.stage]
Then it returns[Event.stage]
And voila, we are back where we were!
"""





import logging
from datetime import datetime

from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters, ContextTypes, \
    CallbackQueryHandler

import Accept
import UserDatabase, EventDatabase
import Event
import Tags

OLD_EVENT, NAME, START_TIME, END_TIME, LOCATION, DESCRIPTION_FI, DESCRIPTION_EN, PRICE, TICKET_LINK_OR_INFO, \
    TICKET_SELL_TIME, OTHER_LINK, ACCESSIBILITY_FI, ACCESSIBILITY_EN, DC, TAGS, SAVE_EVENT = range(16)

STAGE_SAVED = 50
STAGE_SUBMITTED = 99


stages = ["OLD_EVENT", "NAME", "START_TIME", "END_TIME", "LOCATION", "DESCRIPTION_FI", "DESCRIPTION_EN", "PRICE",
          "TICKET_LINK_OR_INFO", "TICKET_SELL_TIME", "OTHER_LINK",
          "ACCESSIBILITY_FI", "ACCESSIBILITY_EN", "DC", "TAGS", "SAVE_EVENT"]

user_prompts = [["Tervetuloa luomaan tapahtumaa. Kirjoittamalla 'back' pääset laittamaan edellisen kentän uudelleen. "
                 "Voit myös editoida tapahtumaa myöhemmin.\n\n"
                 "Pääset pois tapahtuman luonnista kirjoittamalla /cancel milloin vain.\n\n"
                 "Kaikki muutokset tallentuvat automaattisesti ja voit jatkaa tapahtuman luontia siitä mistä jäit valitsemalla "
                 "Luo tapahtuma",
                 "Anna tapahtuman nimi\nJos tapahtuman nimi on sekä suomeksi, että englanniksi "
                    "erota nämä laittamalla // väliin",
                "Milloin tapahtuma alkaa: (päivä.kuukausi.vuosi tunti.minuutti):",
                    "Milloin tapahtuma päättyy?  "
                    "(päivä.kuukausi.vuosi tunti.minuutti) 'skip' jos päättymisaikaa ei tarvita. "
                    "Jos kirjoitat pelkän kellonajan, oletan, että tapahtuma päättyy samana päivänä",
                 "Sijainti: jos sijainnin nimi on eri suomeksi ja englanniksi, erota nämä laittamalla // väliin",
                    "Tapahtumakuvaus suomeksi:",
                    "Tapahtumakuvaus englanniksi:",
                    "Tapahtuman hinta, kirjoita 0, jos tapahtuma on ilmainen.",
                    "Lipunmyyntilinkki tai ohjeet lipun ostamiseen. "
                    "Eroita suomen- ja englanninkieliset ohjeet laittamalla //. 'skip' jos ei tarvita.",
                    "Monelta lipunmyynti alkaa? (päivä.kuukausi.vuosi tunti.minuutti), 'skip' jos ei tarvita.",
                    "Linkki, esimerkiksi Facebook-tapahtumaan. 'skip' jos ei tarvita.",
                    "Saavutettavuusohjeet suomeksi, kirjoita help, jos tarvitset ohjeita.",
                    "Saavutettavuusohjeet englanniksi.",
                    "Dresscode: eroita suomen- ja englanninkieliset ohjeet laittamalla //",
                    "Tunnisteet:",
                    "Kirjoita 'save' jos haluat tallentaa tapahtuman. Voit muokata sitä myöhemmin.\n\n"
                    "Kirjoita 'submit' jos haluat lähettää tapahtuman hyväksyttäväksi. Tapahtumaa ei voi tämän jälkeen enää muuttaa."],
                ["Welcome to creating an event! By writing 'back' you can input the last field again. "
                 "You can also edit the events after it's submitted!\n\nBy typing /cancel, you can leave the creating of the event\n\n"
                 "All changes are saved automatically and you can continue editing the event later from where you left off "
                 "by choosing Create event.",
                 "Please type the name of the event.\n"
                "If there is a different name for finnish and english, "
                    "please separate the names with //",
                "When does the event start: (day.month.year hours.minutes):",
                    "What time does the event end "
                    "(day.month.year hours.minutes) type skip if not needed. "
                    "If you only write the time, I'll assume that the event will end later the same day.",
                 "Location: Separate finnish and english location name with //",
                    "Description in Finnish:",
                    "Description in English:",
                    "Price of the event, write 0, if the event is free.",
                    "Ticket link or purchasing instructions: Separate finnish and english instructions with //. 'skip' if not needed.",
                    "At which time the ticket sale starts? (day.month.year hours.minutes), 'skip' if not needed",
                    "Link, for example for a Facebook event. Type 'skip if not needed'",
                    "Accessibility instructions in Finnish, if you need help for what to write here, type help.",
                    "Accessibility instructions in English.",
                    "Dresscode: please separate the english and finnish dresscode with //",
                    "Tags:",
                    "Type 'save' if you want to save the event. You can return to edit it later.\n\n"
                    "Type 'submit' if you want to send the event to be accepted. After that, you can't edit the event anymore!"]]


def translate_string(string_key, update):
    language_code = UserDatabase.get_user_lang_code(update)
    language_strings = {
        0: {
            "add": "lisää",
            "remove": "poista",
            "save": "tallenna",
            "No tag": "Sinulla ei ole tägejä tapahtumassasi.",
            "no access": "Sinulla ei ole oikeuksia tapahtuman luomiseen.",
            "unsaved event": "Sinulla on tapahtuma/tapahtumia, jota et ole vielä tallentanut.",
            "time machine": "Joko sinulla on aikakone, tai sitten laitoit väärän ajan. Yritä uudestaan :)",
            "correct format": "Anna aika oikeassa muodossa.",
            "correct format2": "Aika on väärässä muodossa. Anna aika (päivä.kuukausi.vuosi tunti.minuutti) -muodossa.",
            "ticket wrong time": "Laitoit ajan, joka on menneisyydessä. Laita aika joka on tulevaisuudessa (edes minuutin päässä).",
            "help": "Ohjeet tulee joskus myöhemmin. Kirjoita saavuttavuusohjeet",
            "submitted": "Tapahtuma tallennettu ja lähetetty LTKY:lle hyväksyttäväksi.",
            "saved": "Tapahtuma tallennettu. Voit muokata tapahtumaa valitsemalla menusta Muokkaa tapahtumaa ja lähettää sen tarkastettavaksi valitsemalla Luo tapahtuma.",
            "cancel": "Toimenpide keskeytetty.",
        },
        1: {
            "add": "add",
            "remove": "remove",
            "save": "save",
            "No tag": "You don't have any tags in your event.",
            "no access": "You have no authorization to create an event.",
            "unsaved event": "You have event(s) that you haven't yet submitted.",
            "time machine": "Either you have a time machine, or then you accidentally put there a wrong time, try again :)",
            "correct format": "Please enter the time in the correct format!",
            "correct format2": "Invalid time format. Please enter the time in (day.month.year hours.minutes) -format.",
            "ticket wrong time": "You've put the ticket sell time that is in the past. Please put a time that is in the future (even by a minute).",
            "help": "Help will be here some day! Write the accessibility instructions.",
            "submitted": "Event saved and submitted for LTKY to check it!",
            "saved": "Event saved. You can edit the event by choosing Edit event from a menu. You can send it by choosing Create event.",
            "cancel": "Action cancelled.",
    }
    }

    return language_strings.get(language_code, language_strings[1]).get(string_key, string_key)



valid_start_date_formats = ["%d.%m.%Y %H:%M", "%d.%m.%Y %H.%M", "%d.%m.%y %H:%M", "%d.%m.%y %H.%M", "%d.%m.%y %H",
                            "%d.%m.%Y %H"]

valid_end_date_formats_full = ["%d.%m.%Y %H:%M", "%d.%m.%Y %H.%M", "%d.%m.%y %H:%M", "%d.%m.%y %H.%M", "%d.%m.%y %H",
                            "%d.%m.%Y %H"]

valid_end_date_formats_time = ["%H:%M", "%H.%M", "%H"]



# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

async def run_before_every_return(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if UserDatabase.get_user_type(update) == 4:
        try:
            event = context.user_data['event']
            try:
                if event.stage == 99:
                    print("The event stage is now COMPLETED!")
                elif event.stage == 50:
                    print("Event stage is now SAVED!")
                else:
                    print(f"The event stage is now: {stages[event.stage]}")
            except TypeError:
                pass

        except KeyError:
            print("Event object not excisting yet")


async def want_to_edit_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if UserDatabase.get_user_lang(update) == "fi":
        reply_keyboard = [["Kyllä", "Ei"]]
        prompt = "Haluatko jatkaa tapahtuman editoimista? Jos et, luonnos poistetaan."

    else:
        reply_keyboard = [["Yes", "No"]]
        prompt = "Do you want to continue editing the event? If not, the draft will be deleted."



    await update.message.reply_text(
        prompt,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Edit events?"
        ),
    )
    ReplyKeyboardRemove()




async def close_keyboard(update, context):
    ReplyKeyboardRemove()

async def create_event_object(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Makes the event object and ads creator and puts 0 as id
    try:
        context.user_data["event"] = Event.Event(0, update.message.from_user.username)
    except AttributeError:
        context.user_data["event"] = Event.Event(0, update.message.from_user.username)
    except IndexError:
        context.user_data["event"] = Event.Event(0, update.message.from_user.username)




async def event_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    #the starting point of the handler

    # checks if its regular user
    if UserDatabase.get_user_type(update) == 1:
        await update.message.reply_text(translate_string("no access", update))
        return ConversationHandler.END

    #checks if there is a event backed up with event stage not set to STAGE_SUBMITTED (99), if is,
    # pops the keyboard and the response goes to old_event()

    event_to_edit = EventDatabase.get_event_to_edit(update.message.from_user.username)

    if event_to_edit is not None:
        await update.message.reply_text(EventDatabase.event_parser_all(event_to_edit))
        await update.message.reply_text(translate_string("unsaved event", update))
        await want_to_edit_keyboard(update, context)
        await run_before_every_return(update, context)
        return OLD_EVENT



    #Creating a new event
    await update.message.reply_text(
        user_prompts[UserDatabase.get_user_lang_code(update)][0]
    )



    #Makes the event object and ads creator and puts 0 as id
    await create_event_object(update, context)

    await update.message.reply_text(f"{user_prompts[UserDatabase.get_user_lang_code(update)][NAME]}")
    await run_before_every_return(update, context)
    return NAME

async def old_event(update: Update, context: ContextTypes.DEFAULT_TYPE)->int:
    await close_keyboard(update, context)

    #If user wants to edit the saved event
    if update.message.text == "Yes" or update.message.text == "Kyllä":
        #Gets the event from the database
        event_to_edit = EventDatabase.get_event_to_edit(update.message.from_user.username)
        context.user_data["event"] = event_to_edit

        #Displays the correct prompt and goes to the correct position on the event making progress
        await update.message.reply_text(fr"{user_prompts[UserDatabase.get_user_lang_code(update)][event_to_edit.stage]}")
        await run_before_every_return(update, context)

        #to pop the tags keyboard :) if needed
        if event_to_edit.stage == TAGS:
            await Tags.full_keyboard(update, context, translate_string("remove", update), translate_string("add", update))
            context.user_data["tag_adding"] = True
        return event_to_edit.stage

    #if user wants to create a new event
    await update.message.reply_text(f"{user_prompts[UserDatabase.get_user_lang_code(update)][NAME]}")
    EventDatabase.event_backup_delete(EventDatabase.get_event_to_edit(update.message.from_user.username))
    await create_event_object(update, context)
    await run_before_every_return(update, context)
    return NAME





async def name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    event = context.user_data['event']
    event.name = update.message.text
    event.stage = START_TIME

    # backup
    EventDatabase.event_backup_save(event, update)

    await update.message.reply_text(f"{user_prompts[UserDatabase.get_user_lang_code(update)][START_TIME]}")
    await run_before_every_return(update, context)
    return START_TIME


async def start_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    user_input = update.message.text
    user_input = user_input.lower()
    if user_input == "back":
        await update.message.reply_text(f"{user_prompts[UserDatabase.get_user_lang_code(update)][NAME]}")
        await run_before_every_return(update, context)
        return NAME

    event = context.user_data['event']

    start_time_text = user_input
    start_time_parsed = None
    try:
        # Parse the input text into a datetime object
        for format_str in valid_start_date_formats:
            try:
                start_time_parsed = datetime.strptime(start_time_text, format_str)
                break
            except ValueError:
                continue

        if start_time_parsed is None:
            raise ValueError

        # checks if the time is in the future
        if datetime.now() > start_time_parsed:
            await update.message.reply_text(translate_string("time machine", update))
            return START_TIME

        event.start_time = start_time_parsed

        # backup
        EventDatabase.event_backup_save(event, update)


        await update.message.reply_text(f"{user_prompts[UserDatabase.get_user_lang_code(update)][END_TIME]}")
        event.stage = END_TIME
        await run_before_every_return(update, context)
        return END_TIME

    except ValueError:

        await update.message.reply_text(f"{translate_string('correct format', update)}\n\n{user_prompts[UserDatabase.get_user_lang_code(update)][START_TIME]}")
        await run_before_every_return(update, context)
        return START_TIME


async def end_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text
    user_input = user_input.lower()
    if user_input == "back":
        await update.message.reply_text(f"{user_prompts[UserDatabase.get_user_lang_code(update)][START_TIME]}")
        await run_before_every_return(update, context)
        return START_TIME

    event = context.user_data['event']
    end_time_text = update.message.text

    if end_time_text.lower() == "skip":
        await update.message.reply_text(f"{user_prompts[UserDatabase.get_user_lang_code(update)][LOCATION]}")
        event.stage = LOCATION
        await run_before_every_return(update, context)
        return LOCATION

    for format_str in valid_end_date_formats_full:
        try:
            end_time_parsed = datetime.strptime(end_time_text, format_str)
            break
        except ValueError:
            continue

    for format_str in valid_end_date_formats_full:
        try:
            end_time_date = event.start_time.strftime("%d.%m.%Y ")
            end_time_parsed_str = end_time_date + end_time_text
            end_time_parsed = datetime.strptime(end_time_parsed_str, format_str)

            break
        except ValueError:
            continue


    if end_time_parsed is None:
        raise ValueError


    try:
        #end_time_parsed = datetime.strptime(end_time_parsed, "%d.%m.%Y %H:%M")
        event.end_time = end_time_parsed

        # backup
        event.stage = LOCATION
        EventDatabase.event_backup_save(event, update)

    except ValueError:
        await update.message.reply_text(translate_string("correct format2", update))
        await run_before_every_return(update, context)
        return END_TIME



    await update.message.reply_text(f"{user_prompts[UserDatabase.get_user_lang_code(update)][LOCATION]}")
    await run_before_every_return(update, context)
    return LOCATION


async def location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text
    user_input = user_input.lower()
    if user_input == "back":
        await update.message.reply_text(f"{user_prompts[UserDatabase.get_user_lang_code(update)][END_TIME]}")
        await run_before_every_return(update, context)
        return END_TIME

    event = context.user_data['event']
    event.location = update.message.text

    # backup
    event.stage = DESCRIPTION_FI
    EventDatabase.event_backup_save(event, update)

    await update.message.reply_text(f"{user_prompts[UserDatabase.get_user_lang_code(update)][DESCRIPTION_FI]}")
    await run_before_every_return(update, context)
    return DESCRIPTION_FI


async def description_fi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text
    user_input = user_input.lower()
    if user_input == "back":
        await update.message.reply_text(f"{user_prompts[UserDatabase.get_user_lang_code(update)][LOCATION]}")
        await run_before_every_return(update, context)
        return LOCATION


    event = context.user_data['event']
    event.description_fi = update.message.text

    # backup
    event.stage = DESCRIPTION_EN
    EventDatabase.event_backup_save(event, update)

    await update.message.reply_text(f"{user_prompts[UserDatabase.get_user_lang_code(update)][DESCRIPTION_EN]}")
    await run_before_every_return(update, context)
    return DESCRIPTION_EN


async def description_en(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text
    user_input = user_input.lower()
    if user_input == "back":
        await update.message.reply_text(f"{user_prompts[UserDatabase.get_user_lang_code(update)][DESCRIPTION_FI]}")
        await run_before_every_return(update, context)
        return DESCRIPTION_FI


    event = context.user_data['event']
    event.description_en = update.message.text

    # backup
    event.stage = PRICE
    EventDatabase.event_backup_save(event, update)

    await update.message.reply_text(f"{user_prompts[UserDatabase.get_user_lang_code(update)][PRICE]}")
    await run_before_every_return(update, context)
    return PRICE


async def price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text
    user_input = user_input.lower()
    if user_input == "back":
        await update.message.reply_text(f"{user_prompts[UserDatabase.get_user_lang_code(update)][DESCRIPTION_EN]}")
        await run_before_every_return(update, context)
        return DESCRIPTION_EN

    event = context.user_data['event']
    try:
        event.price = float(update.message.text)
    except ValueError:
        await update.message.reply_text(f"{user_prompts[UserDatabase.get_user_lang_code(update)][PRICE]}")
        await run_before_every_return(update, context)
        return PRICE

    EventDatabase.event_backup_save(event, update)
    event.stage = TICKET_LINK_OR_INFO
    await update.message.reply_text(f"{user_prompts[UserDatabase.get_user_lang_code(update)][TICKET_LINK_OR_INFO]}")
    await run_before_every_return(update, context)
    return TICKET_LINK_OR_INFO


async def ticket_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text
    user_input = user_input.lower()
    if user_input == "back":
        await update.message.reply_text(f"{user_prompts[UserDatabase.get_user_lang_code(update)][PRICE]}")
        await run_before_every_return(update, context)
        return PRICE

    event = context.user_data['event']

    if user_input == "skip":
        event.ticket_link = None
    else:
        event.ticket_link = update.message.text

    # backup
    event.stage = TICKET_SELL_TIME
    EventDatabase.event_backup_save(event, update)

    await update.message.reply_text(f"{user_prompts[UserDatabase.get_user_lang_code(update)][TICKET_SELL_TIME]}")
    await run_before_every_return(update, context)
    return TICKET_SELL_TIME


async def ticket_sell_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text
    user_input = user_input.lower()
    if user_input == "back":
        await update.message.reply_text(f"{user_prompts[UserDatabase.get_user_lang_code(update)][TICKET_LINK_OR_INFO]}")
        await run_before_every_return(update, context)
        return TICKET_LINK_OR_INFO

    event = context.user_data['event']
    if user_input == "skip":
        event.ticket_sell_time = None

    else:
        sell_time_text = user_input
        sell_time_parsed = None

        try:
            # Parse the input text into a datetime object
            for format_str in valid_start_date_formats:
                try:
                    sell_time_parsed = datetime.strptime(sell_time_text, format_str)
                    break
                except ValueError:
                    continue

            if sell_time_parsed is None:
                await update.message.reply_text(
                    translate_string("ticket wrong time", update))
                return TICKET_SELL_TIME


            # checks if the time is in the future
            if datetime.now() > sell_time_parsed:
                await update.message.reply_text(
                    translate_string("ticket wrong time", update))
                return TICKET_SELL_TIME

            event.ticket_sell_time = sell_time_parsed

            # backup
            EventDatabase.event_backup_save(event, update)

            await update.message.reply_text(f"{user_prompts[UserDatabase.get_user_lang_code(update)][OTHER_LINK]}")
            event.stage = OTHER_LINK
            await run_before_every_return(update, context)
            return OTHER_LINK

        except ValueError:
            await update.message.reply_text(
                f"{translate_string('correct format', update)}\n\n{user_prompts[UserDatabase.get_user_lang_code(update)][TICKET_SELL_TIME]}")
            await run_before_every_return(update, context)
            return TICKET_SELL_TIME


    # backup
    event.stage = OTHER_LINK
    EventDatabase.event_backup_save(event, update)

    await update.message.reply_text(f"{user_prompts[UserDatabase.get_user_lang_code(update)][OTHER_LINK]}")
    await run_before_every_return(update, context)
    return OTHER_LINK


async def other_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text
    user_input = user_input.lower()
    if user_input == "back":

        await update.message.reply_text(user_prompts[UserDatabase.get_user_lang_code(update)][TICKET_SELL_TIME])
        await run_before_every_return(update, context)
        return TICKET_SELL_TIME

    if user_input == "skip":
        await update.message.reply_text(user_prompts[UserDatabase.get_user_lang_code(update)][ACCESSIBILITY_FI])
        await run_before_every_return(update, context)
        return ACCESSIBILITY_FI

    event = context.user_data['event']
    event.other_link = update.message.text

    # backup
    event.stage = ACCESSIBILITY_FI
    EventDatabase.event_backup_save(event, update)

    await update.message.reply_text(user_prompts[UserDatabase.get_user_lang_code(update)][ACCESSIBILITY_FI])
    await run_before_every_return(update, context)
    return ACCESSIBILITY_FI


async def accessibility_fi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text
    user_input = user_input.lower()
    if user_input == "back":
        await update.message.reply_text(user_prompts[UserDatabase.get_user_lang_code(update)][OTHER_LINK])
        await run_before_every_return(update, context)
        return OTHER_LINK

    if user_input == "help":
        await update.message.reply_text(translate_string("help", update))
        await run_before_every_return(update, context)
        return ACCESSIBILITY_FI

    event = context.user_data['event']
    event.accessibility_fi = update.message.text

    # backup
    event.stage = ACCESSIBILITY_EN
    EventDatabase.event_backup_save(event, update)

    await update.message.reply_text("Accessibility instructions in English.")
    await run_before_every_return(update, context)
    return ACCESSIBILITY_EN


async def accessibility_en(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text
    user_input = user_input.lower()
    if user_input == "back":
        await update.message.reply_text(user_prompts[UserDatabase.get_user_lang_code(update)][ACCESSIBILITY_FI])
        await run_before_every_return(update, context)
        return ACCESSIBILITY_FI

    if user_input == "help":
        await update.message.reply_text("Help will be here some day! Write the accessibility instructions in Finnish.")
        await run_before_every_return(update, context)
        return ACCESSIBILITY_EN

    event = context.user_data['event']
    event.accessibility_en = update.message.text

    #backup
    event.stage = DC
    EventDatabase.event_backup_save(event, update)

    await update.message.reply_text(user_prompts[UserDatabase.get_user_lang_code(update)][DC])
    await run_before_every_return(update, context)
    return DC


async def dc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text
    user_input = user_input.lower()
    if user_input == "back":
        await update.message.reply_text(user_prompts[UserDatabase.get_user_lang_code(update)][ACCESSIBILITY_EN])
        await run_before_every_return(update, context)
        return ACCESSIBILITY_EN

    event = context.user_data['event']
    event.dc = update.message.text

    #backup
    event.stage = TAGS
    EventDatabase.event_backup_save(event, update)

    await update.message.reply_text(user_prompts[UserDatabase.get_user_lang_code(update)][TAGS])
    await Tags.full_keyboard(update, context, "remove", "add")
    context.user_data["tag_adding"] = True
    await run_before_every_return(update, context)
    return TAGS


async def tags(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply = update.message.text
    reply = reply.lower()

    event = context.user_data["event"]

    if event.tags == None:
        event.tags = []

    if reply == "add" or reply == "lisää":
        context.user_data["tag_adding"] = True
        await Tags.full_keyboard(update, context, translate_string("remove", update), translate_string("add", update))
        return TAGS

    elif reply == "remove" or reply == "poista":
        await Tags.full_keyboard(update, context, translate_string("add", update), translate_string("remove", update))
        context.user_data["tag_adding"] = False
        return TAGS

    elif reply == "save":
        # backup
        event.stage = SAVE_EVENT
        EventDatabase.event_backup_save(event, update)
        await update.message.reply_text(user_prompts[UserDatabase.get_user_lang_code(update)][SAVE_EVENT])
        await run_before_every_return(update,context)
        return SAVE_EVENT



    #adding tags
    if context.user_data['tag_adding']:
        if reply == "all":
            event.tags = ["all"]
        elif reply not in event.tags:
            try:
                if "all" in event.tags:
                    event.tags.remove("all")
                event.tags.append(reply)
            except AttributeError:
                event.tags = [f"{reply}"]

        await update.message.reply_text(f"{event.tags}")

        await Tags.full_keyboard(update, context, translate_string("remove", update), translate_string("add", update))
        return TAGS

    #removing tags
    if not context.user_data['tag_adding']:
        if reply == "all":
            event.tags = ["all"]
        try:
            event.tags.remove(reply)
        except AttributeError:
            await update.message.reply_text(translate_string("No tag"))

        await update.message.reply_text(f"{event.tags}")
        await Tags.full_keyboard(update, context, translate_string("add", update), translate_string("remove", update))
        return TAGS

    await update.message.reply_text(EventDatabase.event_parser_all(context.user_data['event']))
    await update.message.reply_text(user_prompts[UserDatabase.get_user_lang_code(update)][SAVE_EVENT])
    await run_before_every_return(update, context)
    return SAVE_EVENT


async def save(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text
    user_input = user_input.lower()
    if user_input == "back":
        await update.message.reply_text("Dresscode:")
        await run_before_every_return(update, context)
        return DC

    text = update.message.text.strip()
    choice = text.lower()

    if choice == "submit":
        #event_list = EventDatabase.events_reader("events.json")
        event = context.user_data['event']
        """try:
            event.id = event_list[-1].id + 1
        except IndexError:
            event.id = 1"""

        event.stage = STAGE_SUBMITTED
        #event_list.append(event)
        #EventDatabase.events_writer(event_list)
        event = context.user_data['event']
        event.stage = 99
        await update.message.reply_text(translate_string("submitted", update))
        await update.message.reply_text(EventDatabase.event_parser_all(event))
        #EventDatabase.event_backup_delete(update, context)
        EventDatabase.event_backup_save(event, update)
        await Accept.message_to_admins(context)
        await run_before_every_return(update, context)
        return ConversationHandler.END

    if choice == "save":
        event = context.user_data['event']
        await update.message.reply_text(translate_string("saved", update))
        EventDatabase.event_backup_save(event, update)


        await run_before_every_return(update, context)
        return ConversationHandler.END



async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(translate_string("cancel", update))
    await run_before_every_return(update, context)
    ReplyKeyboardRemove()
    return ConversationHandler.END