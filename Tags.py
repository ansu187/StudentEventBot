from telegram.ext import ContextTypes, ConversationHandler
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove

import UserDatabase
import json
import Filepaths

ADD_REMOVE, ADD, REMOVE, SAVE = range(4)


async def normal_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE, button: str, prompt: str):

    reply_keyboard = get_tag_language_list(update)

    await update.message.reply_text(
        f"{prompt}",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Tags"
        ),
    )

    await close_keyboard(update, context)


async def get_keyboard() -> []:
    try:
        with open(Filepaths.tags_file, 'r') as file:
            tags_data = json.load(file)
            data = tags_data.get('tags', [])
    except Exception:
        print("Something went wrong")
        return None
    reply_keyboard = data
    return reply_keyboard

async def full_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE, button: str, prompt: str):


    reply_keyboard = get_keyboard()
    if reply_keyboard == None:
        return
    reply_keyboard.append(["Save", "/cancel", f"{button}"])

    await update.message.reply_text(
        f"{prompt}",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Event tags"
        ),
    )
    await close_keyboard(update,context)





async def close_keyboard(update, context):
    ReplyKeyboardRemove()


def get_tag_language_list(update):
    user_lang = UserDatabase.get_user_lang(update)
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

    if user_lang == "fi":
        return finnish_tags
    else:
        return english_tags



async def list_tags(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_list = context.user_data["user_list"]
    for user in user_list:
        if user.id == update.message.from_user.id:
            await update.message.reply_text(f"You currently have these tags:\n{user.tags}")


async def start_tags(update: Update, context: ContextTypes.DEFAULT_TYPE): #The command takes you here

    if not UserDatabase.is_user(update):
        await update.message.reply_text("You have no user.")
        return

    # Gets the user list from database
    user_list = UserDatabase.user_reader()
    context.user_data["user_list"] = user_list

    # Keyboard asking if you want to add or remove tags
    reply_keyboard = [["Add", "Remove"]]
    await update.message.reply_text(
        "Do you want to add or remove tags?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Event tags"
        ),
    )

    await close_keyboard(update, context)

    return ADD_REMOVE


async def add_remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Forks into add or remove
    choice = update.message.text
    await list_tags(update, context)
    if choice == "Add":
        await normal_keyboard(update, context, "remove", "What tags do you want to add?")
        return ADD
    if choice == "Remove":
        await normal_keyboard(update, context, "add", "What tags do you want to remove?")
        return REMOVE

    else:
        ReplyKeyboardRemove()

        return ConversationHandler.END


# set tags to all
async def tags_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Removes all the tags and leaves #all
    user_list = context.user_data["user_list"]
    for user in user_list:
        if user.id == update.message.from_user.id:
            user.tags = ["#all"]
            context.user_data["user_list"] = user_list

    await list_tags(update, context)

    await normal_keyboard(update, context, "add", "What tags do you want to remove?")

    return ADD


# adds a new tag
async def add_tag(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    if text == "remove":
        await normal_keyboard(update, context, "add", "What tags do you want to remove?")
        return REMOVE

    user_list = context.user_data["user_list"]
    for user in user_list:
        if user.id == update.message.from_user.id:
            if text not in user.tags:
                user.tags.append(text)
                if "#all" in user.tags:
                    user.tags.remove("#all")
                context.user_data["user_list"] = user_list

    await list_tags(update, context)

    await normal_keyboard(update, context, "remove", "What tags do you want to add?")

    return ADD


# removes a tag
async def remove_tag(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    if text == "add":
        await normal_keyboard(update, context, "remove", "What tags do you want to add?")
        return REMOVE

    user_list = context.user_data["user_list"]
    for user in user_list:
        if user.id == update.message.from_user.id:
            user.tags.remove(text)
            context.user_data["user_list"] = user_list

    await list_tags(update, context)

    await normal_keyboard(update, context, "add", "What tags do you want to remove?")
    return REMOVE


#
async def save_tag(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        UserDatabase.user_writer(context.user_data["user_list"])
        await update.message.reply_text("Your tags have been updated!")

    except KeyError:
        await update.message.reply_text("Please select some tags first!")

    ReplyKeyboardRemove()
    await close_keyboard(update, context)

    return ConversationHandler.END
