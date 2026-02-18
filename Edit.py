
from telegram.ext import ContextTypes, ConversationHandler
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup

from datetime import datetime


import logging

import EventSaver, EventDatabase, Tags, Accept, Filepaths
import MessageSender
import UserDatabase

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

EVENT_SELECTOR, MENU, NAME, START_TIME, END_TIME, LOCATION, DESCRIPTION_FI, DESCRIPTION_EN, PRICE, TICKET_LINK_OR_INFO, \
    TICKET_SELL_TIME, OTHER_LINK, ACCESSIBILITY_FI, ACCESSIBILITY_EN, DC, TAGS, SUBMIT, SHOW_EVENT, APPLY_CHANGES = range(19)

TAG_REMOVING = 22


async def event_to_edit_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE, event_list):
    reply_keyboard = []

    for event in event_list:
        button = [f"{event.name}"]
        reply_keyboard.append(button)

    reply_keyboard.append(["/cancel"])

    await update.message.reply_text(
        f"what event do you want to edit?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Edit events?"
        ),
    )

    ReplyKeyboardRemove()
    return

async def edit_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try: #if this is triggered from the organizer's side
        button_pattern, event_id, event_name, button = query.data.split(";")
    except ValueError: #if this is triggered from the super admin's side
        button_pattern, event_id, button = query.data.split(";")

    if button == "no":
        await query.edit_message_text("Event not edited!")
        return ConversationHandler.END

    
    event_id = int(event_id)

    if event_id == 0:
        context.user_data['event'] = EventDatabase.get_event_by_name_from_backup(
            event_name, query.from_user.username
        )
    else:
        context.user_data['event'] = EventDatabase.get_event_by_id(event_id, Filepaths.events_file)

    await edit_keyboard(update, context)
    return MENU


async def event_selector(update: Update, context: ContextTypes.DEFAULT_TYPE):
    event_list = context.user_data['event_list']
    text = update.message.text.lower()

    for event in event_list:
        event_name = event.name.lower()
        if event_name == text:
            context.user_data['event'] = event

    await edit_keyboard(update, context)
    return MENU


async def edit_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    # checks if its regular user
    if UserDatabase.get_user_type(update) < 2:
        await update.message.reply_text("You're not supposed to know about this command! "
                                        "I will contact the cyber police immediately! \U0001F46E!")
        return ConversationHandler.END

    event_list = EventDatabase.get_events_from_backup(update.message.from_user.username)

    if event_list == []:
        await update.message.reply_text("You don't have any events to edit")
        return ConversationHandler.END

    await event_to_edit_keyboard(update, context, event_list)


    context.user_data['event_list'] = event_list

    return EVENT_SELECTOR


async def edit_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [["Name", "Start time", "End time"], ["Location", "Description Fi", "Description En"], ["Price",
                      "Ticket link or info", "Ticket sell time"], ["Other link",
                      "Accessibility Fi", "Accessibility En"], ["DC", "Tags", "End", "Submit"], ["Show event"]]

    try: #for events that are not yet accepted
        await update.message.reply_text(
            f"All edits will be instantly saved\nSubmit sends the event to be accepted\nWhat do you want to edit?",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True, input_field_placeholder="Edit events?"
            ),
        )
    except: #this is for allready accepted events
        await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text=f"Submit will apply the changes\n\nWhat do you want to edit?",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, input_field_placeholder="Edit events?"),
        )


    ReplyKeyboardRemove()
    return


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang_code = UserDatabase.get_user_lang_code(update)

    event_to_edit = context.user_data['event']

    choice = update.message.text.upper()

    if choice == "NAME":
        await update.message.reply_text(EventSaver.user_prompts[lang_code][EventSaver.NAME])
        return NAME
    
    elif choice == "START TIME":
        await update.message.reply_text(EventSaver.user_prompts[lang_code][EventSaver.START_TIME])
        return START_TIME
    
    elif choice == "END TIME":
        await update.message.reply_text(EventSaver.user_prompts[lang_code][EventSaver.END_TIME])
        return END_TIME
    
    elif choice == "LOCATION":
        await update.message.reply_text(EventSaver.user_prompts[lang_code][EventSaver.LOCATION])
        return LOCATION
    
    elif choice == "DESCRIPTION FI":
        await update.message.reply_text(f"{event_to_edit.description_fi}")
        await update.message.reply_text(EventSaver.user_prompts[lang_code][EventSaver.DESCRIPTION_FI])
        return DESCRIPTION_FI
    
    elif choice == "DESCRIPTION EN":
        await update.message.reply_text(f"{event_to_edit.description_en}")
        await update.message.reply_text(EventSaver.user_prompts[lang_code][EventSaver.DESCRIPTION_EN])
        return DESCRIPTION_EN
    
    elif choice == "PRICE":
        await update.message.reply_text(EventSaver.user_prompts[lang_code][EventSaver.PRICE])
        return PRICE
    
    elif choice == "TICKET LINK OR INFO":
        await update.message.reply_text(EventSaver.user_prompts[lang_code][EventSaver.TICKET_LINK_OR_INFO])
        return TICKET_LINK_OR_INFO
    
    elif choice == "TICKET SELL TIME":
        await update.message.reply_text(EventSaver.user_prompts[lang_code][EventSaver.TICKET_SELL_TIME])
        return TICKET_SELL_TIME
    
    elif choice == "OTHER LINK":
        await update.message.reply_text(EventSaver.user_prompts[lang_code][EventSaver.OTHER_LINK])
        return OTHER_LINK
    
    elif choice == "ACCESSIBILITY FI":
        await update.message.reply_text(f"{event_to_edit.accessibility_fi}")
        await update.message.reply_text(EventSaver.user_prompts[lang_code][EventSaver.ACCESSIBILITY_FI])
        return ACCESSIBILITY_FI
    
    elif choice == "ACCESSIBILITY EN":
        await update.message.reply_text(f"{event_to_edit.accessibility_en}")
        await update.message.reply_text(EventSaver.user_prompts[lang_code][EventSaver.ACCESSIBILITY_EN])
        return ACCESSIBILITY_EN
    
    elif choice == "DC":
        await update.message.reply_text(EventSaver.user_prompts[lang_code][EventSaver.DC])
        return DC
    
    elif choice == "TAGS":
        event_tags = []

        context.user_data["tags"] = event_tags

        reply_markup = InlineKeyboardMarkup(Tags.get_all_tags_keyboard(update, button_code="Edit_tags"))
        await update.message.reply_text(f"Current tags: {event_tags}", reply_markup=reply_markup)
        return TAGS
    
    elif choice == "END":
        await update.message.reply_text("You can submit the event later with /event command")
        return ConversationHandler.END

    elif choice == "SUBMIT":
        event = context.user_data['event']

        #the event is allready sent to users and edited after the fact
        if event.accepted:
            try:
                text = EventDatabase.event_parser_all(event)
                await update.message.reply_text(text)
                
            except Exception:
                text1 = EventDatabase.event_parser_creator_1(event)
                text2 = EventDatabase.event_parser_creator_2(event)
                await update.message.reply_text(text1)
                await update.message.reply_text(text2)


            
            keyboard = [
            [
                InlineKeyboardButton("Yes",
                                    callback_data=f"Edit_event;{event.id};yes"),
                InlineKeyboardButton("No",
                                    callback_data=f"Edit_event;{event.id};no"),]
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(f"Do you want to apply the changes? They will be applied instantly.", 
                                            reply_markup=reply_markup)
            
            return APPLY_CHANGES
                

        #this is for the event that isn't yet public
        await update.message.reply_text("Please type submit, if you want to send this for LTKY to check.\n "
                                        "This is irreversible!")
        return SUBMIT



    elif choice == "SHOW EVENT":
        event = context.user_data['event']
        try:
            await update.message.reply_text(f"{EventDatabase.event_parser_all(event)}")
        except Exception:
            await update.message.reply_text(f"{EventDatabase.event_parser_creator_1(event)}")
            await update.message.reply_text(f"{EventDatabase.event_parser_creator_2(event)}")
        await edit_keyboard(update, context)
        return MENU




async def name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    user_input = update.message.text
    user_input = user_input.lower()
    if user_input == "back":
        await edit_keyboard(update, context)
        return MENU

    event = context.user_data['event']

    event.name = update.message.text

    # backup
    EventDatabase.event_backup_save(event, update)
    await edit_keyboard(update, context)

    return MENU


async def start_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    user_input = update.message.text
    user_input = user_input.lower()
    if user_input == "back":
        await edit_keyboard(update, context)
        return MENU

    event = context.user_data['event']

    start_time_text = update.message.text
    start_time_parsed = None
    try:
        # Parse the input text into a datetime object
        for format_str in EventSaver.valid_start_date_formats:
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

        await edit_keyboard(update, context)

        return MENU

    except ValueError:
        await update.message.reply_text(f"Please enter the time in the correct format!\n\n"
                                        f"{EventSaver.user_prompts[UserDatabase.get_user_lang_code(update)][EventSaver.START_TIME]}")

        return START_TIME


async def end_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text
    user_input = user_input.lower()
    if user_input == "back":
        await edit_keyboard(update, context)
        return MENU

    event = context.user_data['event']
    end_time_text = update.message.text

    for format_str in EventSaver.valid_end_date_formats_full:
        try:
            end_time_parsed = datetime.strptime(end_time_text, format_str)
            break
        except ValueError:
            continue

    for format_str in EventSaver.valid_end_date_formats_full:
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
        event.end_time = end_time_parsed

        # backup
        EventDatabase.event_backup_save(event, update)

    except ValueError:
        await update.message.reply_text("Invalid time format. "
                                        "Please enter the time in (day.month.year hours.minutes) -format.")
        return END_TIME

    await edit_keyboard(update, context)
    return MENU


async def location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text
    user_input = user_input.lower()
    if user_input == "back":
        await edit_keyboard(update, context)
        return MENU

    event = context.user_data['event']
    event.location = update.message.text

    # backup
    EventDatabase.event_backup_save(event, update)

    await edit_keyboard(update, context)
    return MENU


async def description_fi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text
    user_input = user_input.lower()
    if user_input == "back":
        await edit_keyboard(update, context)
        return MENU



    event = context.user_data['event']
    event.description_fi = update.message.text

    # backup

    EventDatabase.event_backup_save(event, update)

    await edit_keyboard(update, context)
    return MENU


async def description_en(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text
    user_input = user_input.lower()
    if user_input == "back":
        await edit_keyboard(update, context)
        return MENU



    event = context.user_data['event']
    event.description_en = update.message.text

    # backup

    EventDatabase.event_backup_save(event, update)

    await edit_keyboard(update, context)
    return MENU


async def price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text
    user_input = user_input.lower()


    event = context.user_data['event']
    try:
        event.price = float(update.message.text)
    except ValueError:
        await update.message.reply_text(EventSaver.user_prompts[UserDatabase.get_user_lang_code(update)][EventSaver.PRICE])

        return PRICE

    
    EventDatabase.event_backup_save(event, update)
    await edit_keyboard(update, context)
    return MENU


async def ticket_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text
    if user_input.startswith("https://"):
        user_input = user_input[len("https://"):]

    user_input_lower = user_input.lower()
    if user_input_lower == "back":
        await edit_keyboard(update, context)
        return MENU

    event = context.user_data['event']
    event.ticket_link = user_input

    # backup
    event.stage = TICKET_SELL_TIME
    EventDatabase.event_backup_save(event, update)

    await edit_keyboard(update, context)
    return MENU


async def ticket_sell_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text
    user_input = user_input.lower()
    if user_input == "back":
        await edit_keyboard(update, context)
        return MENU

    event = context.user_data['event']
    event.ticket_sell_time = update.message.text

    # backup
    EventDatabase.event_backup_save(event, update)

    await edit_keyboard(update, context)
    return MENU


async def other_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text
    user_input = user_input.lower()
    if user_input == "back":
        await edit_keyboard(update, context)
        return MENU


    event = context.user_data['event']
    event.other_link = update.message.text

    # backup
    EventDatabase.event_backup_save(event, update)

    await edit_keyboard(update, context)
    return MENU


async def accessibility_fi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text
    user_input = user_input.lower()
    if user_input == "back":
        await edit_keyboard(update, context)
        return MENU

    if user_input == "help":
        await update.message.reply_text("Help will be here some day! Write the accessibility instructions in Finnish.")
        return ACCESSIBILITY_FI

    event = context.user_data['event']
    event.accessibility_fi = update.message.text

    # backup
    EventDatabase.event_backup_save(event, update)

    await edit_keyboard(update, context)
    return ACCESSIBILITY_EN


async def accessibility_en(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text
    user_input = user_input.lower()
    if user_input == "back":
        await edit_keyboard(update, context)
        return MENU

    event = context.user_data['event']
    event.accessibility_en = update.message.text

    #backup
    EventDatabase.event_backup_save(event, update)

    await edit_keyboard(update, context)
    return MENU


async def dc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text
    user_input = user_input.lower()
    if user_input == "back":
        await edit_keyboard(update, context)
        return MENU

    event = context.user_data['event']
    event.dc = update.message.text

    #backup
    EventDatabase.event_backup_save(event, update)

    await edit_keyboard(update, context)
    return MENU



async def tags(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    query = update.callback_query
    await query.answer()

    button_pattern, tag_chosen = query.data.split(";")

    if tag_chosen == "cancel":
        await query.edit_message_text(f"Updating tags cancelled.")
        
        return MENU
    
    event_tags = context.user_data["tags"]


    if tag_chosen == "save":
        tag_list_to_save = Tags.match_display_tags_to_canonical(event_tags)

        print(tag_list_to_save)
        event = context.user_data['event']
        event.tags = tag_list_to_save

        await query.edit_message_text(f"Tags updated!")

        EventDatabase.event_backup_save(event, update)
        #await query.message.reply_text(user_prompts[UserDatabase.get_user_lang_code(update)][SAVE_EVENT])
        #await query.message.reply_text(EventDatabase.event_parser_all(context.user_data['event']))
        #await run_before_every_return(update,context)
        EventDatabase.event_backup_save(event, update)

        await edit_keyboard(update, context)
        return MENU
      


    
    if tag_chosen in event_tags:
        while tag_chosen in event_tags:
            event_tags.remove(tag_chosen)

    else:
        event_tags.append(tag_chosen)

    await query.edit_message_text(text=f"Your tags: {event_tags}", 
                                  reply_markup=InlineKeyboardMarkup(Tags.get_all_tags_keyboard(update, button_code="Edit_tags")))
    
    
    return TAGS




async def tags_old(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply = update.message.text
    reply = reply.lower()

    event = context.user_data["event"]

    if event.tags == None:
        event.tags = []

    if reply == "add":
        context.user_data["tag_adding"] = True
        await Tags.full_keyboard(update, context, "remove", "add")
        return TAGS

    elif reply == "remove":
        await Tags.full_keyboard(update, context, "add", "remove")
        context.user_data["tag_adding"] = False
        return TAGS

    elif reply == "save":
        # backup

        EventDatabase.event_backup_save(event, update)

        await edit_keyboard(update, context)
        return MENU



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

        await Tags.full_keyboard(update, context, "remove", "add")
        return TAGS

    #removing tags
    if not context.user_data['tag_adding']:
        if reply == "all":
            event.tags = ["all"]
        try:
            event.tags.remove(reply)
        except AttributeError:
            await update.message.reply_text("You don't have that tag in your event!")

        await update.message.reply_text(f"{event.tags}")
        await Tags.normal_keyboard(update, context, "add", "remove")
        return TAGS

    await edit_keyboard(update, context)
    return MENU



async def submit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    user_input = update.message.text
    user_input = user_input.lower()

    if user_input == "submit":
        event = context.user_data['event']
        event.stage = EventSaver.STAGE_SUBMITTED
        await update.message.reply_text(EventSaver.translate_string("submitted", update))

        try:
            await update.message.reply_text(EventDatabase.event_parser_all(event))
        except Exception:
            await update.message.reply_text(EventDatabase.event_parser_creator_1(event))
            await update.message.reply_text(EventDatabase.event_parser_creator_2(event))


        await Accept.message_to_admins(context)
        EventDatabase.event_backup_save(event, update)

        return ConversationHandler.END
    else:
        await edit_keyboard(update,context)
        return MENU


async def apply_changes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    button_pattern, event_id, button = query.data.split(";")

    event = context.user_data['event']

    if button == "yes":
        EventDatabase.save_changes_to_accepted_event(event)
        await query.edit_message_text("Event changes applied!")
        return ConversationHandler.END

    elif button == "no":
        await query.edit_message_text("Event changes discarted!")
        return ConversationHandler.END
