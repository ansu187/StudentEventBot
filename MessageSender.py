import json
import Event, EventDatabase, User, UserDatabase, Tags, Button
from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters, ContextTypes
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from datetime import datetime, timedelta
import asyncio
from contextlib import suppress

import Filepaths

TAGS, TAGS1, MENU, TIME_MENU, NEXT_WEEK, THIS_WEEK, THIS_MONTH, TODAY, LIST_BY_NUMBER = range(9)

async def tags_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_lang_code = UserDatabase.get_user_lang_code(update)

    reply_keyboard = get_tag_language_list(user_lang_code)

    if user_lang_code == 0:
        prompt = "Mitä tapahtumia haluat nähdä?"
    else:
        prompt = "What events do you want to see?"

    await update.message.reply_text(
        f"{prompt}",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Tags"
        ),
    )

    await close_keyboard(update, context)



async def close_keyboard(update, context):
    ReplyKeyboardRemove()

def get_tag_language_list(user_lang_code):
    
    try:
        with open(Filepaths.tags_file, 'r') as file:
            tags_data = json.load(file)
            data = tags_data.get('tags', [])
    except Exception:
        print("Something went wrong")
        return [[]]

    english_tags = []
    finnish_tags = []

    for tag_list in data:
        english_tags_list = []
        finnish_tags_list = []

        for tag in tag_list:
            try:
                english_tag, finnish_tag = tag.split("//")
            except ValueError:
                english_tag = tag
                finnish_tag = tag

            english_tags_list.append(english_tag)
            finnish_tags_list.append(finnish_tag)

        english_tags.append(english_tags_list)
        finnish_tags.append(finnish_tags_list)

    if user_lang_code == 0:
        return finnish_tags
    else:
        return english_tags



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

async def send_all_events(update: Update, context: ContextTypes.DEFAULT_TYPE):
    event_list = EventDatabase.get_accepted_events()
    time_sorted_event_list = sorted(event_list, key=lambda event: event.start_time)

    await send_event_list(update, context, time_sorted_event_list)
    return


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    prompts = ["Millaisia tapahtumia haluat nähdä?", "What kind of events do you want to see?"]

    if text == "Tietyn tyyppiset tapahtumat" or text == "Events of certain type":
        await tags_keyboard(update, context)
        await close_keyboard(update, context)
        return TAGS


    elif text == "Tapahtumat tiettynä ajankohtana" or text == "Events at certain times":
        await time_sort_keyboard(update)
        return TIME_MENU

    elif text == "Kaikki" or text == "All":
        send_all_events(update, context)
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
        await list_this_month(update, context)
        return ConversationHandler.END
    elif text == "Seuraava kuukausi" or text == "Next month":
        await list_next_month(update, context)
        return ConversationHandler.END

async def list_by_tags_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await tags_keyboard(update, context)
    await close_keyboard(update, context)
    return TAGS


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

    next_month = (this_month % 12) + 1

    time_sorted_event_list = sorted(event_list, key=lambda event: event.start_time)
    complete_event_list = []

    for event in time_sorted_event_list:
        if event.start_time.date().month == next_month:
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
    messages_per_second = 5
    interval = 1 / messages_per_second

    for event in event_list:
        
        keyboard = [
            [
                InlineKeyboardButton(Button.translate_string("Link", UserDatabase.get_user_lang_code(update)), callback_data=f"Event;{event.id};{Button.CALENDER_LINK}"),
                InlineKeyboardButton(Button.translate_string("Show more", UserDatabase.get_user_lang_code(update)), callback_data=f"Event;{event.id};{Button.MORE_INFORMATION}")],
                #[InlineKeyboardButton(Button.translate_string("Like", UserDatabase.get_user_lang_code(update)), callback_data=f"Event;{event.id};{Button.LIKE}")]
        ]


        reply_markup = InlineKeyboardMarkup(keyboard)
        await asyncio.sleep(interval)
        await update.message.reply_text(f"{EventDatabase.get_head(event, UserDatabase.get_user_lang_code(update))}",
                                        reply_markup=reply_markup)

    return

def generate_event_calendar_link(event, update):
    if not event.start_time:
        return "Invalid event times"
    if not event.end_time:
        event.end_time = event.start_time + timedelta(hours=1)

    start_str = event.start_time.strftime("%Y%m%dT%H%M%S")
    end_str = event.end_time.strftime("%Y%m%dT%H%M%S")

    link = f"https://www.google.com/calendar/render?action=TEMPLATE&text={event.name.replace(' ', '+')}" \
           f"&dates={start_str}/{end_str}&location=&sf=true&output=xml"
    return link

def generate_ticket_calendar_link(event, update):

    if not event.ticket_sell_time:
        return None

    end_time = event.ticket_sell_time + timedelta(minutes=10)

    start_str = event.start_time.strftime("%Y%m%dT%H%M%S")
    end_str = end_time.strftime("%Y%m%dT%H%M%S")

    link = f"https://www.google.com/calendar/render?action=TEMPLATE&text={event.name.replace(' ', '+')}+" \
           f"{Button.translate_string('Ticket', update)}&dates={start_str}/{end_str}&location=&sf=true&output=xml"
    return link


async def new_event_job_creator(context: ContextTypes.DEFAULT_TYPE):

    event_id = context.job.data

    event = EventDatabase.get_event_by_id(event_id,Filepaths.events_file)

    user_list = UserDatabase.user_reader()
    prompt = ["Uusi tapahtuma lisätty:", "A new event added:"]


    event_fi = EventDatabase.get_head(event, 0)
    event_en = EventDatabase.get_head(event, 1)
    event_list = [event_fi, event_en]

    event_tags = event.tags

    start_time = datetime.now()
    user_counter = 0


    #sends the new event to all users
    for user in user_list:
        try:
            send_message = False


            if user.user_lang == "fi":
                user_lang_code = 0

            else:
                user_lang_code = 1

            keyboard = [
                [
                    InlineKeyboardButton(Button.translate_string("Link", user_lang_code), callback_data=f"Event;{event_id};{Button.CALENDER_LINK}"),
                    InlineKeyboardButton(Button.translate_string("Show more", user_lang_code),
                                         callback_data=f"Event;{event_id};{Button.MORE_INFORMATION}"),
                    #InlineKeyboardButton(Button.translate_string("Like", user_lang_code), callback_data=f"Event;{event_id};{Button.LIKE}")
                ]
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)


            if user.tags == [] or user.tags == ["#all"]: #all is a legacy thing with old users
                send_message = True


            elif set(user.tags) & set(event_tags):
                send_message = True
            

            elif event_tags == []:
                send_message = True

            if send_message:
                await context.bot.send_message(
                    chat_id=user.id, text=f"{prompt[user_lang_code]}\n\n{event_list[user_lang_code]}",
                    reply_markup=reply_markup)

                print(f"Message sent to user {user.id}")
                user_counter += 1

        except Exception as e:
            print(f"Failed to send message to user {user.id}: {str(e)}")


    

    end_time = datetime.now()
    await context.bot.send_message(chat_id=context.job.chat_id, text=f"All messages send in {end_time - start_time} to {user_counter} users!")

    user_id = UserDatabase.get_user_id(event.creator)
    await context.bot.send_message(chat_id=user_id, text=f"The event {event.name} was send to {user_counter} users!")
    



async def send_new_event_to_all(update: Update, context: ContextTypes.DEFAULT_TYPE, event_id):
    context.job_queue.run_once(new_event_job_creator, 0, data=event_id, chat_id=update.message.chat_id)
    return




async def new_message_job_creator(context: ContextTypes):

    message = context.job.data
    

    message_fi, message_en = message.split("//")
    prompt = [message_fi, message_en]

    user_list = UserDatabase.user_reader()


    start_time = datetime.now()
    user_counter = 0

    for user in user_list:
        try:
            if user.user_lang == "fi":
                user_lang_code = 0
            else:
                user_lang_code = 1

            await context.bot.send_message(chat_id=user.id, text=prompt[user_lang_code])


            print(f"Message sent to user {user.id}")
            user_counter += 1

        except Exception as e:
            print(f"Failed to send message to user {user.id}: {str(e)}")


    end_time = datetime.now()
    await context.bot.send_message(chat_id=context.job.chat_id, text=f"All messages send in {end_time - start_time} to {user_counter} users!")


async def send_message_to_all(update: Update, context: ContextTypes.DEFAULT_TYPE, message):
    context.user_data['message_to_all'] = message
    context.user_data['current_user'] = update.message.chat_id

    context.job_queue.run_once(new_message_job_creator, 0, data=message, chat_id=update.message.chat_id)

    return