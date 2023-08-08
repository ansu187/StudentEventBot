import Event, EventDatabase, User, UserDatabase
from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters, ContextTypes
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime, timedelta




async def list(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:
        arguments = context.args
        arguments = " ".join(arguments)
        arguments = arguments.lower()
    except TypeError:
        arguments = ""


    event_list = EventDatabase.get_accepted_events()
    user_lang = UserDatabase.get_user_lang(update)
    if arguments == "id":

        await send_events(update,context, event_list)

    elif arguments == "":
        time_sorted_event_list = sorted(event_list, key=lambda event: event.start_time)

        await send_events(update, context, event_list)

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

    elif arguments == "next week":
        now = datetime.now()
        day = now.date()

        while day.weekday() != 0:
            day = day + timedelta(days=1)

        week_start_date = day
        week_end_date = day + timedelta(days=6)

        time_sorted_event_list = sorted(event_list, key=lambda event: event.start_time)
        complete_event_list = []

        for event in time_sorted_event_list:
            if week_start_date <= event.start_time.date() <= week_end_date:
                await update.message.reply_text(EventDatabase.event_parser_normal(event, user_lang))
                complete_event_list.append(event)

        await send_events(update,context,complete_event_list)






    else:
        await update.message.reply_text("Invalid argument.")



async def send_events(update: Update, context: ContextTypes.DEFAULT_TYPE, event_list):

    user_lang = UserDatabase.get_user_lang(update)
    context.user_data["user_lang"] = user_lang

    for event in event_list:
        keyboard = [
            [
                InlineKeyboardButton("Show:", callback_data=f"{event.id}")]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(f"{EventDatabase.get_head(event.id, UserDatabase.get_user_lang(update))}", reply_markup=reply_markup)






async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    print(query.data)
    try:
        message_id = int(query.data)
        event = EventDatabase.event_finder_by_id(message_id, "events.json")
        await query.edit_message_text(
            text=f"Selected option: {EventDatabase.event_parser_normal(event, context.user_data['user_lang'])}")
    except ValueError:
        await query.edit_message_text("Please give a whole number!")