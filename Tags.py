from telegram.ext import ContextTypes, ConversationHandler
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup

import UserDatabase, User
import json
import Filepaths

SAVE = 0
EDIT = 99




def get_tag_list(): #returns all tags currently in use.
    tag_list = []
    try:
        with open(Filepaths.tags_file, 'r') as file:
            tags_data = json.load(file)
            data = tags_data.get('tags', [])
    except Exception:
        print("Something went wrong")
        return None
    
    for row in data:
        for tag in row:
            tag_list.append(tag)

    return tag_list


def get_tag_list_language(lang_code):
    pre_tag_list = get_tag_list()
    fi_tag_list = []
    en_tag_list = []

    for tag in pre_tag_list:
        en_tag, fi_tag = tag.split("//")
        fi_tag_list.append(fi_tag.strip())
        en_tag_list.append(en_tag.strip())

    if lang_code == 1:
        return en_tag_list
    else:
        return fi_tag_list


def get_user_tag_list(update: Update):
    current_user: User = UserDatabase.get_current_user(update)
    user_lang = UserDatabase.get_user_lang_code(update)

    tag_list = current_user.tags
    fi_tag_list = []
    en_tag_list = []

    for tag in tag_list:
        if tag == "#all":
            continue

        en_tag, fi_tag = tag.split(" // ")
        fi_tag_list.append(fi_tag)
        en_tag_list.append(en_tag)
        
    if user_lang == 0:
        return fi_tag_list
    
    else:
        return en_tag_list



def get_all_tags_keyboard(update: Update, button_code):
    # gets all tags from tags.json
    tag_list = get_tag_list_language(UserDatabase.get_user_lang_code(update))

    keyboard = []
    indented_keyboard = []

    
    counter = 0
    for tag in tag_list:
        counter += 1
        indented_keyboard.append(InlineKeyboardButton(tag, callback_data=f"{button_code};{tag}"))
        if counter % 3 == 0:
            keyboard.append(indented_keyboard)
            indented_keyboard = []
        

    keyboard.append(indented_keyboard)

    keyboard.append([InlineKeyboardButton("Save", callback_data=f"{button_code};save"), 
                     InlineKeyboardButton("Cancel", callback_data=f"{button_code};cancel")])

    return(keyboard)


async def tags(update: Update, context: ContextTypes.DEFAULT_TYPE): #The command takes you here

    if not UserDatabase.is_user(update):
        await update.message.reply_text("You have no user.")
        return

    # Gets the user tags from the database
    user_tag_list = get_user_tag_list(update)

    
    reply_markup = InlineKeyboardMarkup(get_all_tags_keyboard(update, button_code="user_tags"))
    
    await update.message.reply_text(f"Your tags: {user_tag_list}", reply_markup=reply_markup)

    #stores the tag data under the specific user's id, not all in the same spot, 
    #this fucked the tags up previously
    context.user_data[str(update.message.from_user.id)] = user_tag_list

    print (f"the id: {update.message.from_user.id}")

    return EDIT


async def edit_tags(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    query = update.callback_query
    await query.answer()

    button_pattern, tag_chosen = query.data.split(";")

    if tag_chosen == "cancel":
        await query.edit_message_text(f"Updating tags cancelled.")
        
        return ConversationHandler.END
    
    user_tag_list = context.user_data[str(query.from_user.id)]


    if tag_chosen == "save":
        all_tags_in_use = get_tag_list()
        tag_list_to_save = []

        for common_tag in all_tags_in_use:
            for user_tag in user_tag_list:
                if user_tag in common_tag:
                    tag_list_to_save.append(common_tag)

        print(tag_list_to_save)
        UserDatabase.update_tags(tag_list_to_save, query.from_user.id)

        await query.edit_message_text(f"Tags updated!")
                
        return ConversationHandler.END


    
    

    
    if tag_chosen in user_tag_list:
        while tag_chosen in user_tag_list:
            user_tag_list.remove(tag_chosen)

    else:
        user_tag_list.append(tag_chosen)

    await query.edit_message_text(text=f"Your tags: {user_tag_list}", 
                                  reply_markup=InlineKeyboardMarkup(get_all_tags_keyboard(update, button_code="user_tags")))
    
    
    return EDIT


