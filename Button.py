import Event, EventDatabase, User, UserDatabase, Tags, MessageSender, EventLiker
from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters, ContextTypes
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from datetime import datetime, timedelta
import asyncio

import Filepaths

HIDE, DESCRIPTION, MORE_INFORMATION, CALENDER_LINK, EVENT_LINK, TICKET_LINK, LIKE, SHOW_LIKES, EDIT_EVENT = range(9)


def translate_string(string_key, update):
    language_code = UserDatabase.get_user_lang_code(update)

    language_strings = {
        0: {
            "Show more": "Näytä lisää",
            "Hide": "Piilota",
            "Link": "Luo kalenterilinkki",
            "Ticket": "Lipunmyynti",
            "Description": "Näytä kuvaus",
            "Event": "Luo linkki tapahtumalle",
            "Ticket sale": "Luo linkki lipunmyynnille",
            "Like": "Tykkää"

        },
        1: {
            "Show more": "Show more",
            "Hide": "Hide",
            "Link": "Create a calender link",
            "Ticket": "Ticket+sale",
            "Description": "Show description",
            "Event": "Create link for event",
            "Ticket sale": "Create link for tickets"

        }
    }

    return language_strings.get(language_code, language_strings[1]).get(string_key, string_key)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    message_id_str, message_type_str = query.data.split(";")


    try:
        message_id = int(message_id_str)
        button = int(message_type_str)
        event = EventDatabase.event_finder_by_id(message_id, Filepaths.events_file)

        #event buttons

        #puts in the long message
        if button == DESCRIPTION:
            keyboard = [[
                    InlineKeyboardButton(translate_string("Hide", update), callback_data=f"{event.id};{HIDE}")]
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                text=f"{EventDatabase.event_parser_normal(event, UserDatabase.get_user_lang_code(update))}" , reply_markup=reply_markup)

        elif button == MORE_INFORMATION:
            keyboard = [[

                InlineKeyboardButton(translate_string("Description", update), callback_data=f"{event.id};{DESCRIPTION}"),
                InlineKeyboardButton(translate_string("Hide", update), callback_data=f"{event.id};{HIDE}")]
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                text=f"{EventDatabase.event_parser_compact(event, UserDatabase.get_user_lang_code(update))}",
                reply_markup=reply_markup)

        #puts in the short message
        elif button == HIDE:
            #add this button
            keyboard = [
                [
                    InlineKeyboardButton(translate_string("Link", update), callback_data=f"{event.id};{CALENDER_LINK}"),
                    InlineKeyboardButton(translate_string("Show more", update),
                                         callback_data=f"{event.id};{MORE_INFORMATION}")
                ],
            #[InlineKeyboardButton(translate_string("Like", update), callback_data=f"{event.id};{LIKE}")]
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(f"{EventDatabase.get_head(event, UserDatabase.get_user_lang_code(update))}",
                                            reply_markup=reply_markup)

        elif button == CALENDER_LINK:
            keyboard = [[
                InlineKeyboardButton(translate_string("Event", update), callback_data=f"{event.id};{EVENT_LINK}")],
                [InlineKeyboardButton(translate_string("Ticket sale", update), callback_data=f"{event.id};{TICKET_LINK}")],
                [InlineKeyboardButton(translate_string("Hide", update), callback_data=f"{event.id};{HIDE}")]
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                text=f"{EventDatabase.get_head(event, UserDatabase.get_user_lang_code(update))}",
                reply_markup=reply_markup)

        elif button == EVENT_LINK:
            keyboard = [
                [InlineKeyboardButton(translate_string("Hide", update), callback_data=f"{event.id};{HIDE}")]
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.message.edit_text(text=f"{EventDatabase.get_head(event, UserDatabase.get_user_lang_code(update))}"
                                               f"{MessageSender.generate_event_calendar_link(event, update)}",
                                          reply_markup=reply_markup)

        elif button == TICKET_LINK:
            keyboard = [
                [InlineKeyboardButton(translate_string("Hide", update), callback_data=f"{event.id};{HIDE}")]
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.edit_text(text=f"{EventDatabase.get_head(event, UserDatabase.get_user_lang_code(update))}"
                                               f"{MessageSender.generate_ticket_calendar_link(event, update)}",
                                           reply_markup=reply_markup)

        elif button == LIKE:
            EventLiker.event_liker(query.message.from_user.id, event.id)

        elif button == SHOW_LIKES:
            await query.message.reply_text(EventLiker.like_counter(event.id))

    except ValueError:
        await query.edit_message_text("Please give a whole number!")