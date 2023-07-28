from telegram.ext import CommandHandler, ContextTypes, ConversationHandler
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove

import UserDatabase

ADD_REMOVE, ADD, REMOVE, SAVE = range(4)


async def keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE, button: str, prompt: str):
    reply_keyboard = [["all"], ["#alcohol-free", "#sits", "#appro"], ["#bar", "#kellari"],
                      ["Save", "/cancel", f"{button}"]]

    await update.message.reply_text(
        f"What tags do you want to {prompt}?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Event tags"
        ),
    )

    await close_keyboard(update, context)


async def close_keyboard(update, context):
    ReplyKeyboardRemove()


async def list_tags(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_list = context.user_data["user_list"]
    for user in user_list:
        if user.id == update.message.from_user.id:
            await update.message.reply_text(f"You currently have these tags:\n{user.tags}")


async def start_tags(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        await keyboard(update, context, "add", "remove")
        return ADD
    if choice == "Remove":
        await keyboard(update, context, "remove", "add")
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

    await keyboard(update, context, "add")

    return ADD


# adds a new tag
async def add_tag(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_list = context.user_data["user_list"]
    for user in user_list:
        if user.id == update.message.from_user.id:
            if update.message.text not in user.tags:
                user.tags.append(update.message.text)
                if "#all" in user.tags:
                    user.tags.remove("#all")
                context.user_data["user_list"] = user_list

    await list_tags(update, context)

    await keyboard(update, context, "add")

    return ADD


# removes a tag
async def remove_tag(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_list = context.user_data["user_list"]
    for user in user_list:
        if user.id == update.message.from_user.id:
            user.tags.remove(update.message.text)
            context.user_data["user_list"] = user_list

    await list_tags(update, context)

    await keyboard(update, context, "remove")
    await close_keyboard(update, context)
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
