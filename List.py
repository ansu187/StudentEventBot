import Event, EventDatabase, User, UserDatabase, Tags
from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters, ContextTypes
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from datetime import datetime, timedelta
import asyncio

import Filepaths

TAGS, TAGS1, MENU, TIME_MENU, NEXT_WEEK, THIS_WEEK, THIS_MONTH, TODAY, LIST_BY_NUMBER = range(9)
SHORT_MESSAGE, LONG_MESSAGE = 0, 1

def translate_string(string_key, update):
    language_code = UserDatabase.get_user_lang_code(update)
    language_strings = {
        0: {
            "Show more": "Näytä lisää",
            "Hide": "Piilota",

        },
        1: {
            "Show more": "Show more",
            "Hide": "Hide",

    }
    }

    return language_strings.get(language_code, language_strings[1]).get(string_key, string_key)


async def list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompts = [["Mitä tapahtumia haluat nähdä?"],["What events you want to see?"]]
    user_lang = UserDatabase.get_user_lang(update)
    if user_lang == "fi":
        lang_code = 0
        reply_keyboard = [["Tietyn tyyppiset tapahtumat"], ["Tapahtumat tiettynä ajankohtana"], ["Kaikki"], ["/cancel"]]

    else:
        lang_code = 1
        reply_keyboard = [["Events of certain type"], ["Events at certain times"], ["All"], ["/cancel"]]

    await update.message.reply_text(
        f"{prompts[lang_code][0]}?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Menu:"
        ),
    )

    ReplyKeyboardRemove()
    return MENU



async def time_sort_keyboard(update: Update):
    prompts = [["Miltä ajalta haluat tapahtumat?"], ["From what time do you want the events?"]]
    user_lang = UserDatabase.get_user_lang(update)
    if user_lang == "fi":
        lang_code = 0
        reply_keyboard = [["Tämä viikko"], ["Seuraava viikko"], ["Tämä kuukausi"],["Seuraava kuukausi"], ["/cancel"]]

    else:
        lang_code = 1
        reply_keyboard = [["This week"], ["Next week"], ["This month"],["Next month"], ["/cancel"]]

    await update.message.reply_text(
        f"{prompts[lang_code][0]}?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Menu:"
        ),
    )

    ReplyKeyboardRemove()
    return

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    prompts = ["Millaisia tapahtumia haluat nähdä?", "What kind of events do you want to see?"]

    if text == "Tietyn tyyppiset tapahtumat" or text == "Events of certain type":
        await Tags.normal_keyboard(update, context, "", prompts[UserDatabase.get_user_lang_code(update)])
        await Tags.close_keyboard(update, context)
        return TAGS


    elif text == "Tapahtumat tiettynä ajankohtana" or text == "Events at certain times":
        await time_sort_keyboard(update)
        return TIME_MENU

    elif text == "Kaikki" or text == "All":
        event_list = EventDatabase.get_accepted_events()
        time_sorted_event_list = sorted(event_list, key=lambda event: event.start_time)

        await send_event_list(update, context, time_sorted_event_list)
        return ConversationHandler.END


async def time_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "Tämä viikko" or text == "This week":
        await list_this_week(update,context)
        return ConversationHandler.END
    elif text == "Seuraava viikko" or text == "Next week":
        await list_next_week(update,context)
        return ConversationHandler.END
    elif text == "Tämä kuukausi" or text == "This month":
        await list_next_month(update, context)
        return ConversationHandler.END
    elif text == "Seuraava kuukausi" or text == "Next month":
        await list_next_month(update, context)
        return ConversationHandler.END




async def list_by_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_lang = UserDatabase.get_user_lang(update)
    if user_lang == "fi":
        await update.message.reply_text("Kuinka monta tapahtumaa haluat nähdä?")

    else:
        await update.message.reply_text("How many events do you want to see?")
    return LIST_BY_NUMBER

async def list_by_number1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    event_list = EventDatabase.get_accepted_events()

    try:
        arguments = int(update.message.text)
    except TypeError:
        await update.message.reply_text("Please give a whole number!")
        return ConversationHandler.END


    complete_event_list = []
    time_sorted_event_list = sorted(event_list, key=lambda event: event.start_time)
    i = 0
    for event in time_sorted_event_list:
        complete_event_list.append(event)
        i += 1
        if i >= arguments:
            break
    await send_event_list(update, context, complete_event_list)



async def list_this_week(update: Update, context: ContextTypes.DEFAULT_TYPE):
    event_list = EventDatabase.get_accepted_events()
    now = datetime.now().isocalendar()[1]

    time_sorted_event_list = sorted(event_list, key=lambda event: event.start_time)
    complete_event_list = []

    for event in time_sorted_event_list:
        if event.start_time.date().isocalendar()[1] == now:
            complete_event_list.append(event)

    await send_event_list(update, context, complete_event_list)
    if not complete_event_list:
        user_lang = UserDatabase.get_user_lang(update)
        if user_lang == "fi":
            await update.message.reply_text("Ei tapahtumia kyseisenä aikana.")
        else:
            await update.message.reply_text("No events at that time.")
        return ConversationHandler.END

    return ConversationHandler.END
async def list_this_month(update: Update, context: ContextTypes.DEFAULT_TYPE):
    event_list = EventDatabase.get_accepted_events()
    this_month = datetime.now().month

    time_sorted_event_list = sorted(event_list, key=lambda event: event.start_time)
    complete_event_list = []

    for event in time_sorted_event_list:
        if event.start_time.date().month == this_month:
            complete_event_list.append(event)

    await send_event_list(update, context, complete_event_list)
    if not complete_event_list:
        user_lang = UserDatabase.get_user_lang(update)
        if user_lang == "fi":
            await update.message.reply_text("Ei tapahtumia kyseisenä aikana.")
        else:
            await update.message.reply_text("No events at that time.")
        return ConversationHandler.END

    return ConversationHandler.END


async def list_next_week(update: Update, context: ContextTypes.DEFAULT_TYPE):
    event_list = EventDatabase.get_accepted_events()
    now = datetime.now().isocalendar()[1]

    time_sorted_event_list = sorted(event_list, key=lambda event: event.start_time)
    complete_event_list = []

    for event in time_sorted_event_list:
        if event.start_time.date().isocalendar()[1] == now+1:
            complete_event_list.append(event)

    await send_event_list(update, context, complete_event_list)
    if not complete_event_list:
        user_lang = UserDatabase.get_user_lang(update)
        if user_lang == "fi":
            await update.message.reply_text("Ei tapahtumia kyseisenä aikana.")
        else:
            await update.message.reply_text("No events at that time.")
        return ConversationHandler.END

    return ConversationHandler.END


async def list_next_month(update: Update, context: ContextTypes.DEFAULT_TYPE):
    event_list = EventDatabase.get_accepted_events()
    this_month = datetime.now().month

    time_sorted_event_list = sorted(event_list, key=lambda event: event.start_time)
    complete_event_list = []

    for event in time_sorted_event_list:
        if event.start_time.date().month == this_month+1:
            complete_event_list.append(event)

    if not complete_event_list:
        user_lang = UserDatabase.get_user_lang(update)
        if user_lang == "fi":
            await update.message.reply_text("Ei tapahtumia kyseisenä aikana.")
        else:
            await update.message.reply_text("No events at that time.")
        return ConversationHandler.END


    await send_event_list(update, context, complete_event_list)
    return ConversationHandler.END


async def list_by_tags(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompts = ["Tämän tyyppisiä tapahtumia ei löytynyt.", "No this kind of events found."]
    event_list = EventDatabase.get_event_by_tag(update.message.text)
    if event_list is not None:
        await send_event_list(update, context, event_list)

    else:
        await update.message.reply_text(prompts[UserDatabase.get_user_lang_code(update)])
    return ConversationHandler.END

async def send_event_list(update: Update, context: ContextTypes.DEFAULT_TYPE, event_list):

    user_lang = UserDatabase.get_user_lang(update)
    context.user_data["user_lang"] = user_lang
    messages_per_second = 2
    interval = 1 / messages_per_second

    for event in event_list:
        keyboard = [
            [
                InlineKeyboardButton(translate_string("Show more", update), callback_data=f"{event.id};{SHORT_MESSAGE}")]
        ]


        reply_markup = InlineKeyboardMarkup(keyboard)
        await asyncio.sleep(interval)
        await update.message.reply_text(f"{EventDatabase.get_head(event.id, UserDatabase.get_user_lang(update))}", reply_markup=reply_markup)

    return



async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    message_id_str, message_type_str = query.data.split(";")


    try:
        message_id = int(message_id_str)
        message_type = int(message_type_str)
        event = EventDatabase.event_finder_by_id(message_id, Filepaths.events_file)
        if message_type == SHORT_MESSAGE:
            keyboard = [
                [
                    InlineKeyboardButton(translate_string("Hide", update), callback_data=f"{event.id};{LONG_MESSAGE}")]
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                text=f"{EventDatabase.event_parser_normal(event, UserDatabase.get_user_lang(update))}" , reply_markup=reply_markup)
        if message_type == LONG_MESSAGE:
            keyboard = [
                [
                    InlineKeyboardButton(translate_string("Show more", update), callback_data=f"{event.id};{SHORT_MESSAGE}")]
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(f"{EventDatabase.get_head(event.id, UserDatabase.get_user_lang(update))}",
                                            reply_markup=reply_markup)

    except ValueError:
        await query.edit_message_text("Please give a whole number!")


async def send_new_event_to_all(update: Update, context: ContextTypes.DEFAULT_TYPE, event_id):
    user_list = UserDatabase.user_reader()
    prompt = ["Uusi tapahtuma lisätty:", "A new event added:"]

    #event_fi = EventDatabase.event_parser_normal(EventDatabase.event_finder_by_id(id, Filepaths.events_file), "fi")
    #event_en = EventDatabase.event_parser_normal(EventDatabase.event_finder_by_id(id, Filepaths.events_file), "en")
    #event_text_list = [event_fi, event_en]

    messages_per_second = 20
    interval = 1/messages_per_second

    for user in user_list:
        try:

            keyboard = [
                [
                    InlineKeyboardButton(translate_string("Show more", update), callback_data=f"{event_id}")]
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)
            await context.bot.send_message(chat_id=user.id, text=prompt[UserDatabase.get_user_lang_code(update)])
            await context.bot.send_message(chat_id=user.id, text=f"{EventDatabase.get_head(event_id, UserDatabase.get_user_lang(update))}", reply_markup=reply_markup)

            print(f"Message sent to user {user.id}")

            await asyncio.sleep(interval)
        except Exception as e:
            print(f"Failed to send message to user {user.id}: {str(e)}")