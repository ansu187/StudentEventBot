import Event, EventDatabase, User, UserDatabase, Tags
from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters, ContextTypes
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from datetime import datetime, timedelta
import asyncio

TAGS, TAGS1, MENU, TIME_MENU, NEXT_WEEK, THIS_WEEK, THIS_MONTH, TODAY, LIST_BY_NUMBER = range(9)

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



    event_list = EventDatabase.get_accepted_events()
    user_lang = UserDatabase.get_user_lang(update)
    if arguments == "id":

        await send_events(update,context, event_list)




    elif arguments.startswith("#"):
        time_sorted_event_list = sorted(event_list, key=lambda event: event.start_time)
        for event in time_sorted_event_list:
            try:
                if arguments in event.tags:
                    await update.message.reply_text(EventDatabase.event_parser_normal(event, user_lang))
            except TypeError:
                continue

    elif arguments.isdigit():
        try:
            arguments = int(arguments)
            complete_event_list = []
            time_sorted_event_list = sorted(event_list, key=lambda event: event.start_time)
            i = 0
            for event in time_sorted_event_list:
                complete_event_list.append(event)
                i+=1
                if i >= arguments:
                    break
            await send_events(update, context, complete_event_list)

        except TypeError:
            await update.message.reply_text("Please give a whole number!")



    else:
        await update.message.reply_text("Invalid argument.")

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

    if text == "Tietyn tyyppiset tapahtumat" or text == "Events of certain type":
        await Tags.keyboard(update, context, "", "")
        await Tags.close_keyboard(update, context)
        return TAGS


    elif text == "Tapahtumat tiettynä ajankohtana" or text == "Events at certain times":
        await time_sort_keyboard(update)
        return TIME_MENU

    elif text == "Kaikki" or text == "All":
        event_list = EventDatabase.get_accepted_events()
        time_sorted_event_list = sorted(event_list, key=lambda event: event.start_time)

        await send_events(update, context, time_sorted_event_list)
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
    await send_events(update, context, complete_event_list)



async def list_this_week(update: Update, context: ContextTypes.DEFAULT_TYPE):
    event_list = EventDatabase.get_accepted_events()
    now = datetime.now().isocalendar()[1]

    time_sorted_event_list = sorted(event_list, key=lambda event: event.start_time)
    complete_event_list = []

    for event in time_sorted_event_list:
        if event.start_time.date().isocalendar()[1] == now:
            complete_event_list.append(event)

    await send_events(update, context, complete_event_list)
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

    await send_events(update, context, complete_event_list)
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

    await send_events(update, context, complete_event_list)
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


    await send_events(update, context, complete_event_list)
    return ConversationHandler.END

async def send_events(update: Update, context: ContextTypes.DEFAULT_TYPE, event_list):

    user_lang = UserDatabase.get_user_lang(update)
    context.user_data["user_lang"] = user_lang
    messages_per_second = 2
    interval = 1 / messages_per_second

    for event in event_list:
        keyboard = [
            [
                InlineKeyboardButton("Show:", callback_data=f"{event.id}")]
        ]


        reply_markup = InlineKeyboardMarkup(keyboard)
        await asyncio.sleep(interval)
        await update.message.reply_text(f"{EventDatabase.get_head(event.id, UserDatabase.get_user_lang(update))}", reply_markup=reply_markup)

    return


async def list_by_tags(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_events(update,context, EventDatabase.get_event_by_tag(update.message.text))
    return ConversationHandler.END



async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    try:
        message_id = int(query.data)
        event = EventDatabase.event_finder_by_id(message_id, "events.json")
        await query.edit_message_text(
            text=f"{EventDatabase.event_parser_normal(event, context.user_data['user_lang'])}")
    except ValueError:
        await query.edit_message_text("Please give a whole number!")