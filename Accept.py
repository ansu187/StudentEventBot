import Filepaths
import UserDatabase
from telegram import Update, ReplyKeyboardRemove, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
import EventDatabase
import asyncio

EVENT_SELECTOR, DECISION, REPLY = range(3)



async def send_message_to_all_users(update: Update, context: ContextTypes.DEFAULT_TYPE, id):
    user_list = UserDatabase.user_reader()

    event_fi = EventDatabase.event_parser_normal(EventDatabase.event_finder_by_id(id, Filepaths.events_file), "fi")

    messages_per_second = 20
    interval = 1/messages_per_second

    for user in user_list:
        try:
            await context.bot.send_message(chat_id=user.id, text=event_fi)
            print(f"Message sent to user {user.id}")

            await asyncio.sleep(interval)
        except Exception as e:
            print(f"Failed to send message to user {user.id}: {str(e)}")


async def choose_event_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE, event_list):
    reply_keyboard = []

    for event in event_list:
        button = [f"{event.name}"]
        reply_keyboard.append(button)

    reply_keyboard.append(["/cancel"])

    await update.message.reply_text(
        f"what event do you want to check?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Select event"
        ),
    )

    ReplyKeyboardRemove()

async def accept(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not UserDatabase.is_user(update):
        await update.message.reply_text("You have no user.")
        return

    if UserDatabase.get_user_type(update) < 3:
        await update.message.reply_text("You have no authorization to accept events!")
        return

    event_list = EventDatabase.get_unaccepted_events()
    if not event_list:
        return ConversationHandler.END

    await choose_event_keyboard(update, context, event_list)
    context.user_data['event_list'] = event_list

    return EVENT_SELECTOR


async def accept_decline_keyboard(update):
    reply_keyboard = [["Accept", "Decline"], ["/cancel"]]
    await update.message.reply_text(
        f"What do you want to do with this event?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Select event"
        ),
    )

    ReplyKeyboardRemove()

    return
async def event_selector(update: Update, context: ContextTypes.DEFAULT_TYPE):
    event_list = context.user_data['event_list']
    text = update.message.text.lower()
    for event in event_list:
        event_name = event.name.lower()
        if event_name == text:
            context.user_data['event'] = event

    await update.message.reply_text("Here is the event, what do you want to do with it?")
    try:
        await update.message.reply_text(f"{EventDatabase.event_parser_all(context.user_data['event'])}")
    except Exception:
        await update.message.reply_text(f"{EventDatabase.event_parser_creator_1(context.user_data['event'])}")
        await update.message.reply_text(f"{EventDatabase.event_parser_creator_2(context.user_data['event'])}")

    await accept_decline_keyboard(update)

    return DECISION



async def decision(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    if text == "accept":
        event = context.user_data['event']
        event.accepted = True

        event_list = EventDatabase.events_reader(Filepaths.events_file)
        try:
            event.id = event_list[-1].id + 1
        except IndexError:
            event.id = 1

        event_list.append(event)
        EventDatabase.events_writer(event_list)
        EventDatabase.event_backup_delete(event)
        await update.message.reply_text(f"Event {event.name} accepted!")

        message_to_user = f"Your event {event.name} has been accepted!"

        await send_message_to_all_users(update, context, event.id)

        user_id = UserDatabase.get_user_id(event.creator)
        try:
            await context.bot.send_message(chat_id=user_id, text=message_to_user)
            print(f"Message sent to user {user_id}")

        except Exception as e:
            print(f"Failed to send message to user {user_id}: {str(e)}")



    elif text == "decline":
        event = context.user_data['event']

        event.stage = 50 #so it wont be visible for admins before being re-submitted!

        await update.message.reply_text("Please tell what was wrong with the event:")
        EventDatabase.event_backup_save(event, update)
        return REPLY

    else:
        await update.message.reply_text("Please")

    return ConversationHandler.END



async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    event = context.user_data['event']
    text = f"There was a problem with event {event.name}\n\nUse Edit event in your menu to edit it!\n\nThe problem:"


    text += update.message.text

    user_id = UserDatabase.get_user_id(event.creator)
    try:
        await context.bot.send_message(chat_id=user_id, text=text)
        print(f"Message sent to user {user_id}")

    except Exception as e:
        print(f"Failed to send message to user {user_id}: {str(e)}")

    await update.message.reply_text("Message send to user!")

    return ConversationHandler.END



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

            await context.bot.send_message(chat_id=user.id, text=f"There are {count} events that haven't been accepted.")
            print(f"Message sent to user {user.id}")

            await asyncio.sleep(interval)
        except Exception as e:
            print(f"Failed to send message to user {user.id}: {str(e)}")
