from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, ContextTypes

import MessageSender, UserDatabase, Tags, EventDatabase, Button
import json
import Filepaths
import asyncio

MENU, ADD_TAGS, REMOVE_TAGS, USER_COUNT, CHANGE_USER_TYPE_1, CHANGE_USER_TYPE_2, LIST_USERS, SEND_MESSAGE, EVENT_CHOSEN, DELETE_EVENT = range(10)
USER_TYPE = ["", "normal", "organizer", "admin", "super_admin"]


async def dev(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if UserDatabase.get_user_type(update) < 4:
        return ConversationHandler.END



    reply_keyboard = [["add_tags", "remove_tags"], ["user_count", "change_user_type"],
                      ["list users", "show feedback", "delete feedback"], ["send message to all", "show active events"]]
    await update.message.reply_text(
        f"What do you want to do?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Event tags"
        ),
    )
    ReplyKeyboardRemove()

    return MENU



async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "add_tags":
        await update.message.reply_text("What tag do you want to add?")
        return ADD_TAGS

    elif text == "remove_tags":
        await Tags.normal_keyboard(update, context, "add", "remove from the tag-list")
        return REMOVE_TAGS

    elif text == "user_count":
        await user_count(update, context)
        return ConversationHandler.END

    elif text == "change_user_type":
        await update.message.reply_text("Username:")
        return CHANGE_USER_TYPE_1

    elif text == "list users":
        reply_keyboard = [["all users", "normal users"], ["organizers", "admins"],
                          ["super admins"]]
        await update.message.reply_text(
            f"What do you want to do?",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True, input_field_placeholder="List users"
            ),
        )
        ReplyKeyboardRemove()
        return LIST_USERS

    elif text == "show feedback":
        await show_feedback(update,context)
        return ConversationHandler.END

    elif text == "delete feedback":
        await delete_feedback(update, context)
        return ConversationHandler.END

    elif text == "send message to all":
        await update.message.reply_text("Please type the message, separate finnish and english with //")
        return SEND_MESSAGE
    
    elif text == "show active events":
        event_list = EventDatabase.get_accepted_events()


        user_lang_code = UserDatabase.get_user_lang_code(update)

        for event in event_list:
            keyboard = [
                [
                    InlineKeyboardButton(Button.translate_string("Show likes", update),
                                        callback_data=f"Dev;{event.id};likes"),
                    InlineKeyboardButton(Button.translate_string("Edit event", update),
                                        callback_data=f"Dev;{event.id};edit"),
                                        InlineKeyboardButton("Delete event",
                                        callback_data=f"Dev;{event.id};delete")]
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(f"{EventDatabase.get_head(event, user_lang_code)}", reply_markup=reply_markup)


        return EVENT_CHOSEN



    else:
        await update.message.reply_text("Please use the keyboard. If everything stops working, please type /cancel")
        return ConversationHandler.END


async def event_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    button_pattern, event_id, button  = query.data.split(";")

    event_id = int(event_id)

    if button == "delete":
        
        keyboard = [
            [
                InlineKeyboardButton(Button.translate_string("Yes", update),
                                    callback_data=f"My_events;{event_id};yes"),
                                    InlineKeyboardButton(Button.translate_string("No", update),
                                    callback_data=f"My_events;{event_id};no")]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(f"Do you want to delete the event?", reply_markup=reply_markup)
        
        return DELETE_EVENT
    
    elif button == "edit":
        keyboard = [
            [
                InlineKeyboardButton(Button.translate_string("Yes", update),
                                    callback_data=f"Edit_event;{event_id};yes"),
                                    InlineKeyboardButton(Button.translate_string("No", update),
                                    callback_data=f"Edit_event;{event_id};no")]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(f"Do you want to edit the event?", reply_markup=reply_markup)
        
        return ConversationHandler.END


    return
    event_list = context.user_data['event_list']
    text = update.message.text.lower()

    for event in event_list:
        event_name = event.name.lower()
        if event_name == text:
            context.user_data['event'] = event

    event = context.user_data['event']

    

    await query.edit_message_text(f"{EventDatabase.get_head(event, UserDatabase.get_user_lang_code(update))}", reply_markup=reply_markup)



async def event_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    button_pattern, event_id, button  = query.data.split(";")

    event_id = int(event_id)

    if button == "yes":
        EventDatabase.delete_event(event_id)
        await query.edit_message_text(f"Event deleted!")
        return ConversationHandler.END

    elif button == "no":
        await query.edit_message_text(f"Event not deleted!")
        return ConversationHandler.END


async def show_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    messages_per_second = 15
    interval = 1 / messages_per_second
    try:
        with open(Filepaths.feedback_file, "r") as file:
            for line in file:
                feedback = line.strip()
                if feedback:
                    await update.message.reply_text(feedback)
                    await asyncio.sleep(interval)
                else:
                    await update.message.reply_text("That's all feedback there is!")

    except FileNotFoundError:
        await update.message.reply_text(f"Feedback file '{Filepaths.feedback_file}' not found.")

    return ConversationHandler.END

async def delete_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    messages_per_second = 15
    interval = 1 / messages_per_second
    try:
        with open(Filepaths.feedback_file, "r") as file:
            for line in file:
                feedback = line.strip()
                if feedback:
                    await update.message.reply_text(feedback)
                    await asyncio.sleep(interval)


    except FileNotFoundError:
        await update.message.reply_text(f"Feedback file '{Filepaths.feedback_file}' not found.")
        return ConversationHandler.END

    try:
        with open(Filepaths.feedback_file, "w") as file:
            await update.message.reply_text("Feedbacks deleted!")

    except FileNotFoundError:
        await update.message.reply_text("Weird shit just happened!")

    return ConversationHandler.END


async def send_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await MessageSender.send_message_to_all(update,context,update.message.text)
    return ConversationHandler.END



async def add_tag(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    try:
        with open(Filepaths.tags_file, 'r') as file:
            data = json.load(file)
            tags_list = data.get('tags', [])

            for sub_list in tags_list:
                for tag in sub_list:
                    if tag == text:
                        await update.message.reply_text(f"Tag {text} is already in the tags.")
                        return ConversationHandler.END #Change this into correct one!!!


            # Append the attribute_value to the last list in chunks of 3 strings
            last_list = tags_list[-1] if tags_list else []
            if len(last_list) < 3:
                last_list.append(text)
            else:
                tags_list.append([text])

            data['tags'] = tags_list

        with open(Filepaths.tags_file, 'w') as file:
            json.dump(data, file, indent=2)

        await update.message.reply_text(f"Attribute '{text}' added to tags.json.")

    except (FileNotFoundError, json.JSONDecodeError):
        await update.message.reply_text("Error: Unable to modify tags.json.")

    return ConversationHandler.END


async def remove_tag(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "add":
        await update.message.reply_text("What tag do you want to add?")
        return ADD_TAGS
    try:
        with open(Filepaths.tags_file, 'r') as file:
            data = json.load(file)

        # Step 2: Remove variable text's string from each array
        for tag_list in data['tags']:
            if text in tag_list:
                tag_list.remove(text)

        # Step 3: Refactor arrays to have three strings each, except for the first and last arrays
        for i in range(1, len(data['tags']) - 1):
            while len(data['tags'][i]) > 3:
                data['tags'][i + 1].insert(0, data['tags'][i].pop())

        # Step 4: Write the updated JSON data back to the file
        with open("tags.json", 'w') as file:
            json.dump(data, file, indent=2)

    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        print("Error: Unable to refactor the JSON file.")

    await Tags.normal_keyboard(update, context, "add", "remove from the tag-list")


    return REMOVE_TAGS



async def check_for_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_list = UserDatabase.user_reader()
    text = update.message.text
    text = text.lower()

    users_to_remove = []
    for user in user_list:
        try:
            user_nick = user.nick.lower()
        except Exception:
            continue

        if user_nick == text:
            context.user_data['user'] = user
            users_to_remove.append(user)

    for user in users_to_remove:
        user_list.remove(user)

    UserDatabase.user_writer(user_list)
    try:
        user = context.user_data['user']
    except KeyError:
        await update.message.reply_text(f"User {text} not found.")
        return ConversationHandler.END

    await update.message.reply_text(f"{user.nick} is currently {USER_TYPE[user.user_type]}\n\n")

    reply_keyboard = [["Normal", "Organizer"], ["Admin", "Super_admin"], ["Cancel"]]
    await update.message.reply_text(
        f"What do you want to set their type to?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Event tags"
        ),
    )
    ReplyKeyboardRemove()

    return CHANGE_USER_TYPE_2

async def set_user_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    text = text.lower()
    user = context.user_data['user']
    if text == "cancel":
        return ConversationHandler.END

    if text == "normal":
        user.user_type = 1
    elif text == "organizer":
        user.user_type = 2
    elif text == "admin":
        user.user_type = 3
    elif text == "super_admin":
        user.user_type = 4

    user_list = UserDatabase.user_reader()

    user_list.append(user)

    UserDatabase.user_writer(user_list)

    await update.message.reply_text(f"{user.nick}'s user type has changed to {USER_TYPE[user.user_type]}!")

    return ConversationHandler.END


async def user_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_list = UserDatabase.user_reader()
    count = 0
    for user in user_list:
        count += 1

    await update.message.reply_text(f"There are currently {count} users!")

    return ConversationHandler.END



async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_list = UserDatabase.user_reader()

    text = update.message.text

    messages_per_second = 15
    interval = 1 / messages_per_second

    if text == "all users":
        await update.message.reply_text("Here are all the users:")
        for user in user_list:
            await update.message.reply_text(f"Username: {user.nick} Type: {user.user_type} Lang: {user.user_lang}")
            await asyncio.sleep(interval)
        return ConversationHandler.END

    elif text == "normal users":
        await update.message.reply_text("Here are all the normal users:")
        for user in user_list:
            if user.user_type == 1:
                await update.message.reply_text(f"Username: {user.nick} Lang: {user.user_lang}")
                await asyncio.sleep(interval)
        return ConversationHandler.END

    elif text == "organizers":
        await update.message.reply_text("Here are all the organizers:")
        for user in user_list:
            if user.user_type == 2:
                await update.message.reply_text(f"Username: {user.nick} Lang: {user.user_lang}")
                await asyncio.sleep(interval)
        return ConversationHandler.END

    elif text == "admins":
        await update.message.reply_text("Here are all the admins:")
        for user in user_list:
            if user.user_type == 3:
                await update.message.reply_text(f"Username: {user.nick} Lang: {user.user_lang}")
                await asyncio.sleep(interval)
        return ConversationHandler.END

    elif text == "super admins":
        await update.message.reply_text("Here are all the super admins:")
        for user in user_list:
            if user.user_type == 4:
                await update.message.reply_text(f"Username: {user.nick} Lang: {user.user_lang}")
                await asyncio.sleep(interval)
        return ConversationHandler.END