from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler, ContextTypes

import UserDatabase, Tags
import json


MENU, ADD_TAGS, REMOVE_TAGS, USER_COUNT, CHANGE_USER_TYPE_1, CHANGE_USER_TYPE_2 = range(6)
USER_TYPE = ["", "normal", "organizer", "admin", "super_admin"]


async def dev(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if UserDatabase.get_user_type(update) < 4:
        return ConversationHandler.END



    reply_keyboard = [["add_tags", "remove_tags"], ["user_count", "change_user_type"]]
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
    print(text)
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

    else:
        await update.message.reply_text("Please use the keyboard. If everything stops working, please type /cancel")

async def add_tag(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    try:
        with open('tags.json', 'r') as file:
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

        with open('tags.json', 'w') as file:
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
        with open("tags.json", 'r') as file:
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
        if user.nick.lower() == text:
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

    await update.message.reply_text(f"The user is currently {USER_TYPE[user.user_type]}\n\n")

    reply_keyboard = [["Normal", "Organizer"], ["Admin", "Super-admin"], ["Cancel"]]
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