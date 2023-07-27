import Event, EventDatabase, User, UserDatabase
from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters, ContextTypes
from telegram import Update
from datetime import datetime, timedelta




async def list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    arguments = context.args
    arguments = " ".join(arguments)
    arguments = arguments.lower()



    event_list = EventDatabase.get_accepted_events()
    user_lang = UserDatabase.get_user_lang(update)
    if arguments == "id":
        for event in event_list:
            await update.message.reply_text(EventDatabase.event_parser_normal(event, user_lang))

    elif arguments == "":
        time_sorted_event_list = sorted(event_list, key=lambda event: event.start_time)
        print(time_sorted_event_list)

        for event in time_sorted_event_list:
            await update.message.reply_text(EventDatabase.event_parser_normal(event, user_lang))

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
            time_sorted_event_list = sorted(event_list, key=lambda event: event.start_time)
            i = 0
            for event in time_sorted_event_list:
                await update.message.reply_text(EventDatabase.event_parser_normal(event, user_lang))
                i+=1
                if i >= arguments:
                    break

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

        for event in time_sorted_event_list:
            if week_start_date <= event.start_time.date() <= week_end_date:
                await update.message.reply_text(EventDatabase.event_parser_normal(event, user_lang))








    else:
        await update.message.reply_text("Invalid argument.")