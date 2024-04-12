import Event, EventDatabase, User, UserDatabase, Tags, Button
from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters, ContextTypes
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from datetime import datetime, timedelta
import asyncio

import Filepaths

CHOICE, OUTPUT, DELETE_EVENT = range(3)

#entry point
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):

    event_list = EventDatabase.get_events_by_creator(update)


    user_lang_code = UserDatabase.get_user_lang_code(update)

    for event in event_list:
        keyboard = [
            [
                InlineKeyboardButton(Button.translate_string("Show likes", user_lang_code),
                                    callback_data=f"My_events;{event.id};{event.name};likes"),
                InlineKeyboardButton(Button.translate_string("Edit event", user_lang_code),
                                    callback_data=f"My_events;{event.id};{event.name};edit"),
                                    InlineKeyboardButton("Delete event",
                                    callback_data=f"My_events;{event.id};{event.name};delete")]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        accepted_text = ""
        if event.accepted:
            accepted_text = "This event is public.\n\n"
        else:
            accepted_text = "This event is not public.\n\n"

        await update.message.reply_text(f"{accepted_text}{EventDatabase.get_head(event, user_lang_code)}", reply_markup=reply_markup)


    return CHOICE





async def choice(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    button_pattern, event_id, event_name, button  = query.data.split(";")

    event_id = int(event_id)

    if button == "delete":
        
        keyboard = [
            [
                InlineKeyboardButton(Button.translate_string("Yes", update),
                                    callback_data=f"My_events;{event_id};{event_name};yes"),
                                    InlineKeyboardButton(Button.translate_string("No", update),
                                    callback_data=f"My_events;{event_id};{event_name};no")]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(f"Do you want to delete the event?", reply_markup=reply_markup)
        
        return DELETE_EVENT
    
    elif button == "edit":
        keyboard = [
            [
                InlineKeyboardButton(Button.translate_string("Yes", UserDatabase.get_user_lang_code(update)),
                                    callback_data=f"Edit_event;{event_id};{event_name};yes"),
                                    InlineKeyboardButton(Button.translate_string("No", UserDatabase.get_user_lang_code(update)),
                                    callback_data=f"Edit_event;{event_id};{event_name};no")]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(f"Do you want to edit the event?", reply_markup=reply_markup)
        
        return ConversationHandler.END



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

    button_pattern, event_id, event_name, button  = query.data.split(";")

    event_id = int(event_id)

    #aka if event is in the event backups
    if event_id == 0:
        if button == "yes":
            EventDatabase.event_backup_delete(EventDatabase.get_event_by_name_from_backup(event_name))
            await query.edit_message_text(f"Event deleted!")
            return ConversationHandler.END
        elif button == "no":
            await query.edit_message_text(f"Event not deleted!")
            return ConversationHandler.END

    else:    
        if button == "yes":
            EventDatabase.delete_event(event_id)
            await query.edit_message_text(f"Event deleted!")
            return ConversationHandler.END

        elif button == "no":
            await query.edit_message_text(f"Event not deleted!")
            return ConversationHandler.END




async def event_to_edit_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE, event_list):
    reply_keyboard = []

    for event in event_list:
        button = [f"{event.name}"]
        reply_keyboard.append(button)

    reply_keyboard.append(["/cancel"])

    await update.message.reply_text(
        f"what event do you want to check?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Choose an event?"
        ),
    )

    ReplyKeyboardRemove()
    return






