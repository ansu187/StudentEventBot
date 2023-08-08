from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters, ContextTypes, \
    CallbackQueryHandler
import UserDatabase, EventDatabase, Event


async def dev(update: Update, context: ContextTypes.DEFAULT_TYPE):
    event_list = EventDatabase.get_accepted_events()
    user_lang = UserDatabase.get_user_lang(update)
    context.user_data["user_lang"] = user_lang

    for event in event_list:
        keyboard = [
            [
                InlineKeyboardButton("Show:", callback_data=f"{event.id}")]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(f"{EventDatabase.get_head(event.id, UserDatabase.get_user_lang(update))}", reply_markup=reply_markup)






async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    await query.answer()

    print(query.data)
    try:
        message_id = int(query.data)
        event = EventDatabase.event_finder_by_id(message_id, "events.json")
        await query.edit_message_text(
            text=f"Selected option: {EventDatabase.event_parser_normal(event, context.user_data['user_lang'])}")
    except ValueError:
        await query.edit_message_text("Please give a whole number!")
