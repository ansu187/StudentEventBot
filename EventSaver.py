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
import Event, UserDatabase, EventDatabase
import Tags

OLD_EVENT, NAME, START_TIME, END_TIME, LOCATION, DESCRIPTION_FI, DESCRIPTION_EN, PRICE, TICKET_LINK, \
    TICKET_SELL_TIME, OTHER_LINK, ACCESSIBILITY_FI, ACCESSIBILITY_EN, DC, TAGS, SAVE_EVENT = range(16)

stages = ["OLD_EVENT", "NAME", "START_TIME", "END_TIME", "LOCATION", "DESCRIPTION_FI", "DESCRIPTION_EN", "PRICE",
          "TICKET_LINK", "TICKET_SELL_TIME", "OTHER_LINK",
          "ACCESSIBILITY_FI", "ACCESSIBILITY_EN", "DC", "TAGS", "SAVE_EVENT"]

user_prompts = ["", "Name of the event:", "When does the event start: (day.month.year hours.minutes):",
                    "What time does the event end "
                    "(day.month.year hours.minutes) type skip if not needed. "
                    "If you only write the time, I'll assume that the event will end later the same day.", "Location:",
                    "Description in Finnish:",
                    "Description in English:",
                    "Price of the event, write 0, if the event is free.",
                    "Ticket link or purchasing instructions:",
                    "At which time the ticket sale starts? (day.month.year hours.minutes)",
                    "Link, for example for a Facebook event:",
                    "Accessibility instructions in Finnish, if you need help for what to write here, type help.",
                    "Accessibility instructions in English.",
                    "Dresscode:",
                    "Tags:",
                    "Type 'save' if you want to save the event. You can return to edit it later.\n\n"
                    "Type 'submit' if you want to send the event to be accepted."]


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
                print(f"The event stage is now: {stages[event.stage]}")
            except TypeError:
                pass

        except KeyError:
            print("Event object not excisting yet")


async def want_to_edit_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [["Yes", "No"]]

    await update.message.reply_text(
        f"Do you want to continue editing the event?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Edit events?"
        ),
    )



async def close_keyboard(update, context):
    ReplyKeyboardRemove()




async def edit_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = ["NAME", "START_TIME", "END_TIME", "LOCATION", "DESCRIPTION_FI", "DESCRIPTION_EN", "PRICE", "TICKET_LINK", \
    "TICKET_SELL_TIME", "OTHER_LINK", "ACCESSIBILITY_FI", "ACCESSIBILITY_EN", "DC"]

    await update.message.reply_text(
        f"Do you want to continue editing the event?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Edit events?"
        ),
    )


async def create_event_object(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Makes the event object and ads creator and puts 0 as id
    try:
        context.user_data["event"] = Event.Event(0, update.message.from_user.username)
    except AttributeError:
        context.user_data["event"] = Event.Event(0, update.message.from_user.username)
    except IndexError:
        context.user_data["event"] = Event.Event(0, update.message.from_user.username)

async def get_events_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """# Gets events and puts them into context
    event_list = EventDatabase.events_reader("events.json")
    context.user_data["event_list"] = event_list"""


async def event_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # checks if its regular user
    if UserDatabase.get_user_type(update) == 1:
        await update.message.reply_text("You have no authorization to create an event.")
        return ConversationHandler.END

    #checks if there is a event backed up, if is, pops the keyboard and the response goes to old_event()
    event_to_edit = EventDatabase.get_event_to_edit(update.message.from_user.username)
    if event_to_edit is not None:
        await update.message.reply_text(EventDatabase.event_parser_all(event_to_edit))
        await update.message.reply_text("You have an event that you haven't yet submitted. What do you want to do with it?")
        await want_to_edit_keyboard(update, context)
        await run_before_every_return(update, context)
        return OLD_EVENT



    #Welcome
    await update.message.reply_text(
        "Welcome to creating an event! By writing 'back' you can input the last field again. You can also edit the events after it's submitted!"
    )
    await get_events_list(update, context)


    #Makes the event object and ads creator and puts 0 as id
    await create_event_object(update, context)

    await update.message.reply_text(f"{user_prompts[NAME]}")
    await run_before_every_return(update, context)
    return NAME

async def old_event(update: Update, context: ContextTypes.DEFAULT_TYPE)->int:
    await close_keyboard(update, context)

    #If user wants to edit the saved event
    if update.message.text == "Yes":
        #Gets the event from the database
        event_to_edit = EventDatabase.get_event_to_edit(update.message.from_user.username)
        context.user_data["event"] = event_to_edit

        #Displays the correct prompt and goes to the correct position on the event making progress
        await update.message.reply_text(fr"{user_prompts[event_to_edit.stage]}")
        await run_before_every_return(update, context)

        #to pop the tags keyboard :)
        if event_to_edit.stage == TAGS:
            await Tags.keyboard(update, context, "remove", "add")
            context.user_data["tag_adding"] = True
        return event_to_edit.stage

    await update.message.reply_text(f"{user_prompts[NAME]}")
    await EventDatabase.event_backup_delete(update, context)
    await get_events_list(update, context)
    await create_event_object(update, context)
    await run_before_every_return(update, context)
    return NAME

async def name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    event = context.user_data['event']

    event.name = update.message.text
    event.stage = START_TIME

    # backup
    EventDatabase.event_backup_save(event, update)

    await update.message.reply_text(f"{user_prompts[START_TIME]}")
    await run_before_every_return(update, context)
    return START_TIME


async def start_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    user_input = update.message.text
    user_input = user_input.lower()
    if user_input == "back":
        await update.message.reply_text(f"{user_prompts[NAME]}")
        await run_before_every_return(update, context)
        return NAME

    event = context.user_data['event']

    start_time_text = update.message.text
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
            await update.message.reply_text(
                "Either you have a time machine, or then you accidentally put there a wrong time, try again")
            return START_TIME

        event.start_time = start_time_parsed

        # backup
        EventDatabase.event_backup_save(event, update)


        await update.message.reply_text(f"{user_prompts[END_TIME]}")
        event.stage = END_TIME
        await run_before_every_return(update, context)
        return END_TIME

    except ValueError:
        await update.message.reply_text(f"Please enter the time in the correct format!\n\n{user_prompts[START_TIME]}")
        await run_before_every_return(update, context)
        return START_TIME


async def end_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text
    user_input = user_input.lower()
    if user_input == "back":
        await update.message.reply_text(f"{user_prompts[START_TIME]}")
        await run_before_every_return(update, context)
        return START_TIME

    event = context.user_data['event']
    end_time_text = update.message.text

    if end_time_text.lower() == "skip":
        await update.message.reply_text(f"{user_prompts[LOCATION]}")
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
        await update.message.reply_text("Invalid time format. Please enter the time in (day.month.year hours.minutes) -format.")
        await run_before_every_return(update, context)
        return END_TIME



    await update.message.reply_text(f"{user_prompts[LOCATION]}")
    await run_before_every_return(update, context)
    return LOCATION


async def location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text
    user_input = user_input.lower()
    if user_input == "back":
        await update.message.reply_text(f"{user_prompts[END_TIME]}")
        await run_before_every_return(update, context)
        return END_TIME

    event = context.user_data['event']
    event.location = update.message.text

    # backup
    event.stage = DESCRIPTION_FI
    EventDatabase.event_backup_save(event, update)

    await update.message.reply_text(f"{user_prompts[DESCRIPTION_FI]}")
    await run_before_every_return(update, context)
    return DESCRIPTION_FI


async def description_fi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text
    user_input = user_input.lower()
    if user_input == "back":
        await update.message.reply_text(f"{user_prompts[LOCATION]}")
        await run_before_every_return(update, context)
        return LOCATION

    if len(user_input) > 240:
        await update.message.reply_text(f"The maximum length of the event is 240 characters. "
                                        f"Your input was {len(user_input) - 240} characters too long! "
                                        f"Please write the Description again.")
        await run_before_every_return(update, context)
        return DESCRIPTION_FI

    event = context.user_data['event']
    event.description_fi = update.message.text

    # backup
    event.stage = DESCRIPTION_EN
    EventDatabase.event_backup_save(event, update)

    await update.message.reply_text(f"{user_prompts[DESCRIPTION_EN]}")
    await run_before_every_return(update, context)
    return DESCRIPTION_EN


async def description_en(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text
    user_input = user_input.lower()
    if user_input == "back":
        await update.message.reply_text(f"{user_prompts[DESCRIPTION_FI]}")
        await run_before_every_return(update, context)
        return DESCRIPTION_FI

    if len(user_input) > 240:
        await update.message.reply_text(f"The maximum length of the event is 240 characters. "
                                        f"Your input was {len(user_input) - 240} characters too long! "
                                        f"Please write the Description again.")
        await run_before_every_return(update, context)
        return DESCRIPTION_EN

    event = context.user_data['event']
    event.description_en = update.message.text

    # backup
    event.stage = PRICE
    EventDatabase.event_backup_save(event, update)

    await update.message.reply_text(f"{user_prompts[PRICE]}")
    await run_before_every_return(update, context)
    return PRICE


async def price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text
    user_input = user_input.lower()
    if user_input == "back":
        await update.message.reply_text(f"{user_prompts[DESCRIPTION_EN]}")
        await run_before_every_return(update, context)
        return DESCRIPTION_EN

    event = context.user_data['event']
    try:
        event.price = float(update.message.text)
    except ValueError:
        await update.message.reply_text(f"{user_prompts[PRICE]}")
        await run_before_every_return(update, context)
        return PRICE

    if event.price == 0:
        context.user_data['free_event'] = True #in order to handle back command right!

        #removes possible information if it's filled for some reason
        event = context.user_data['event']
        event.ticket_sell_time = None
        event.ticket_link = None

        # backup
        event.stage = OTHER_LINK
        EventDatabase.event_backup_save(event, update)

        await update.message.reply_text(f"{user_prompts[OTHER_LINK]}")
        await run_before_every_return(update, context)
        return OTHER_LINK
    else:
        context.user_data['free_event'] = False #in order to handle back command right!
        event.stage = TICKET_LINK
        await update.message.reply_text(f"{user_prompts[TICKET_LINK]}")
        await run_before_every_return(update, context)
        return TICKET_LINK


async def ticket_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text
    user_input = user_input.lower()
    if user_input == "back":
        await update.message.reply_text(f"{user_prompts[PRICE]}")
        await run_before_every_return(update, context)
        return PRICE

    event = context.user_data['event']
    event.ticket_link = update.message.text

    # backup
    event.stage = TICKET_SELL_TIME
    EventDatabase.event_backup_save(event, update)

    await update.message.reply_text(f"{user_prompts[TICKET_SELL_TIME]}")
    await run_before_every_return(update, context)
    return TICKET_SELL_TIME


async def ticket_sell_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text
    user_input = user_input.lower()
    if user_input == "back":
        await update.message.reply_text(f"{user_prompts[TICKET_LINK]}")
        await run_before_every_return(update, context)
        return TICKET_LINK

    event = context.user_data['event']
    event.ticket_sell_time = update.message.text

    # backup
    event.stage = OTHER_LINK
    EventDatabase.event_backup_save(event, update)

    await update.message.reply_text(f"{user_prompts[OTHER_LINK]}")
    await run_before_every_return(update, context)
    return OTHER_LINK


async def other_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text
    user_input = user_input.lower()
    if user_input == "back":
        if context.user_data["free_event"]:
            await update.message.reply_text("Price of the event, write 0, if the event is free.")
            await run_before_every_return(update, context)
            return PRICE
        else:
            await update.message.reply_text("At which time the ticket sale starts? (day.month.year hours.minutes)")
            await run_before_every_return(update, context)
            return TICKET_SELL_TIME

    if user_input == "skip":
        await update.message.reply_text("Accessibility instructions in Finnish, if you need help for what to write here, type help.")
        await run_before_every_return(update, context)
        return ACCESSIBILITY_FI

    event = context.user_data['event']
    event.other_link = update.message.text

    # backup
    event.stage = ACCESSIBILITY_FI
    EventDatabase.event_backup_save(event, update)

    await update.message.reply_text("Accessibility instructions in Finnish, if you need help for what to write here, type help.")
    await run_before_every_return(update, context)
    return ACCESSIBILITY_FI


async def accessibility_fi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text
    user_input = user_input.lower()
    if user_input == "back":
        await update.message.reply_text("Other link, for example for a Facebook event:")
        await run_before_every_return(update, context)
        return OTHER_LINK

    if user_input == "help":
        await update.message.reply_text("Help will be here some day! Write the accessibility instructions in Finnish.")
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
        await update.message.reply_text("Accessibility instructions in Finnish, if you need help for what to write here, type help.")
        await run_before_every_return(update, context)
        return ACCESSIBILITY_FI

    event = context.user_data['event']
    event.accessibility_en = update.message.text

    #backup
    event.stage = DC
    EventDatabase.event_backup_save(event, update)

    await update.message.reply_text("Dresscode:")
    await run_before_every_return(update, context)
    return DC


async def dc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text
    user_input = user_input.lower()
    if user_input == "back":
        await update.message.reply_text("Accessibility instructions in English.")
        await run_before_every_return(update, context)
        return ACCESSIBILITY_EN

    event = context.user_data['event']
    event.dc = update.message.text

    #backup
    event.stage = TAGS
    EventDatabase.event_backup_save(event, update)

    await update.message.reply_text(user_prompts[TAGS])
    await Tags.keyboard(update, context, "remove", "add")
    context.user_data["tag_adding"] = True
    await run_before_every_return(update, context)
    return TAGS


async def tags(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply = update.message.text
    reply = reply.lower()

    event = context.user_data["event"]

    if event.tags == None:
        event.tags = []

    if reply == "add":
        context.user_data["tag_adding"] = True
        await Tags.keyboard(update, context, "remove")
        return TAGS

    elif reply == "remove":
        await Tags.keyboard(update, context, "add")
        context.user_data["tag_adding"] = False
        return TAGS

    elif reply == "save":
        # backup
        event.stage = SAVE_EVENT
        EventDatabase.event_backup_save(event, update)
        await update.message.reply_text(user_prompts[SAVE_EVENT])
        await run_before_every_return(update,context)
        return SAVE_EVENT



    #adding tags
    if context.user_data['tag_adding']:
        if reply == "all":
            event.tags = ["#all"]
        elif reply not in event.tags:
            try:
                if "#all" in event.tags:
                    event.tags.remove("#all")
                event.tags.append(reply)
            except AttributeError:
                event.tags = [f"{reply}"]

        await update.message.reply_text(f"{event.tags}")

        await Tags.keyboard(update, context, "remove", "add")
        return TAGS

    #removing tags
    if not context.user_data['tag_adding']:
        if reply == "all":
            event.tags = ["#all"]
        try:
            event.tags.remove(reply)
        except AttributeError:
            await update.message.reply_text("You don't have that tag in your event!")

        await update.message.reply_text(f"{event.tags}")
        await Tags.keyboard(update,context, "add", "remove")
        return TAGS

    await update.message.reply_text(EventDatabase.event_parser_all(context.user_data['event']))
    await update.message.reply_text(user_prompts[SAVE_EVENT])
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
        event_list = EventDatabase.events_reader("events.json")
        event = context.user_data['event']
        try:
            event.id = event_list[-1].id + 1
        except IndexError:
            event.id = 1
        event_list.append(event)
        EventDatabase.events_writer(event_list)
        event = context.user_data['event']
        await update.message.reply_text(
            f"Event saved and submitted for LTKY to check it!")
        await update.message.reply_text(EventDatabase.event_parser_all(event))
        await EventDatabase.event_backup_delete(update, context)
        await run_before_every_return(update, context)
        return ConversationHandler.END

    if choice == "save":

        await update.message.reply_text("Event saved. Type /edit to edit the event. To submit the event, type /event")
        await run_before_every_return(update, context)
        return ConversationHandler.END



async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.")
    await run_before_every_return(update, context)
    return ConversationHandler.END