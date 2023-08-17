import UserDatabase
from telegram import Update
from telegram.ext import ContextTypes
import EventDatabase
import asyncio


async def send_message_to_all_users(update: Update, context: ContextTypes.DEFAULT_TYPE, id):
    user_list = UserDatabase.user_reader()

    event_fi = EventDatabase.event_parser_normal(EventDatabase.event_finder_by_id(id, "events.json"), "fi")

    messages_per_second = 20
    interval = 1/messages_per_second

    for user in user_list:
        try:
            await context.bot.send_message(chat_id=user.id, text=event_fi)
            print(f"Message sent to user {user.id}")

            await asyncio.sleep(interval)
        except Exception as e:
            print(f"Failed to send message to user {user.id}: {str(e)}")


async def accept(update: Update, context: ContextTypes.DEFAULT_TYPE):
    arguments = context.args

    if UserDatabase.get_user_type(update) < 3:
        await update.message.reply_text("You have no authorization to accept events!")
        return

    if arguments:
        if arguments[0].isdigit():
            id = int(arguments[0])
            event_list = EventDatabase.events_reader("events.json")
            for event in event_list:
                if event.id == id:
                    event.accepted = True
                    EventDatabase.events_writer(event_list)
                    break
            await send_message_to_all_users(update, context, id)

        else:
            await update.message.reply_text("Please add a valid event ID as an argument")



    else:
        event_list = EventDatabase.get_unaccepted_events()
        for event in event_list:

            await update.message.reply_text(EventDatabase.event_parser_all(event))




async def message_to_admins(context: ContextTypes.DEFAULT_TYPE):
    #Sends message to every admin when a new event is created
    admin_list = UserDatabase.get_admins()

    messages_per_second = 20
    interval = 1 / messages_per_second

    unaccepted_events = EventDatabase.get_unaccepted_events()
    count = 0
    for event in unaccepted_events:
        count += 1

    for user in admin_list:
        try:

            await context.bot.send_message(chat_id=user.id, text=f"There is {count} events that haven't been accepted.")
            print(f"Message sent to user {user.id}")

            await asyncio.sleep(interval)
        except Exception as e:
            print(f"Failed to send message to user {user.id}: {str(e)}")
