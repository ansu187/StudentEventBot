from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

import Feedback
import EventSaver
import Start, Tags, List, Accept, Help, Edit, Dev, Menu
import Secrets

USERNAME: Final = "biletestibot"

# Event states
ADD_REMOVE, ADD, REMOVE = range(3)


def main() -> None:
    application = Application.builder().token(Secrets.TOKEN).build()



    # Conversation handler for handling the creation of events
    event_handler = ConversationHandler(
        entry_points=[CommandHandler("event", EventSaver.event_command), MessageHandler(filters.Regex("^(Luo tapahtuma|Create event)$"), EventSaver.event_command)],
        states={
            EventSaver.OLD_EVENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, EventSaver.old_event)],
            EventSaver.NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, EventSaver.name)],
            EventSaver.START_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, EventSaver.start_time)],
            EventSaver.END_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, EventSaver.end_time)],
            EventSaver.TICKET_SELL_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, EventSaver.ticket_sell_time)],
            EventSaver.LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, EventSaver.location)],
            EventSaver.DESCRIPTION_FI: [MessageHandler(filters.TEXT & ~filters.COMMAND, EventSaver.description_fi)],
            EventSaver.DESCRIPTION_EN: [MessageHandler(filters.TEXT & ~filters.COMMAND, EventSaver.description_en)],
            EventSaver.PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, EventSaver.price)],
            EventSaver.TICKET_LINK_OR_INFO: [MessageHandler(filters.TEXT & ~filters.COMMAND, EventSaver.ticket_link)],
            EventSaver.OTHER_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, EventSaver.other_link)],
            EventSaver.ACCESSIBILITY_FI: [MessageHandler(filters.TEXT & ~filters.COMMAND, EventSaver.accessibility_fi)],
            EventSaver.ACCESSIBILITY_EN: [MessageHandler(filters.TEXT & ~filters.COMMAND, EventSaver.accessibility_en)],
            EventSaver.DC: [MessageHandler(filters.TEXT & ~filters.COMMAND, EventSaver.dc)],
            EventSaver.TAGS: [MessageHandler(filters.TEXT & ~filters.COMMAND, EventSaver.tags)],
            EventSaver.SAVE_EVENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, EventSaver.save)],
        },
        fallbacks=[CommandHandler("cancel", EventSaver.cancel)],
    )

    edit_handler = ConversationHandler(
        entry_points=[CommandHandler("edit", Edit.edit_command), MessageHandler(filters.Regex("^(Edit event|Muokkaa tapahtumaa)$"), Edit.edit_command)],
        states={
            Edit.MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, Edit.menu)],
            Edit.NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, Edit.name)],
            Edit.START_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, Edit.start_time)],
            Edit.END_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, Edit.end_time)],
            Edit.TICKET_SELL_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, Edit.ticket_sell_time)],
            Edit.LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, Edit.location)],
            Edit.DESCRIPTION_FI: [MessageHandler(filters.TEXT & ~filters.COMMAND, Edit.description_fi)],
            Edit.DESCRIPTION_EN: [MessageHandler(filters.TEXT & ~filters.COMMAND, Edit.description_en)],
            Edit.PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, Edit.price)],
            Edit.TICKET_LINK_OR_INFO: [MessageHandler(filters.TEXT & ~filters.COMMAND, Edit.ticket_link)],
            Edit.OTHER_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, Edit.other_link)],
            Edit.ACCESSIBILITY_FI: [MessageHandler(filters.TEXT & ~filters.COMMAND, Edit.accessibility_fi)],
            Edit.ACCESSIBILITY_EN: [MessageHandler(filters.TEXT & ~filters.COMMAND, Edit.accessibility_en)],
            Edit.DC: [MessageHandler(filters.TEXT & ~filters.COMMAND,Edit.dc)],
            Edit.TAGS: [MessageHandler(filters.TEXT & ~filters.COMMAND, Edit.tags)],
            Edit.SUBMIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, Edit.submit)],
        },
        fallbacks=[CommandHandler("cancel", EventSaver.cancel)],
    )

    tag_handler = ConversationHandler(
        entry_points=[CommandHandler("tags", Tags.start_tags)],
        states={
            ADD_REMOVE: [MessageHandler(filters.Regex("^(Add|Remove)$"), Tags.add_remove)],
            ADD: [MessageHandler(filters.Regex(r"^(?!all$|Save$)(#\w+)$"), Tags.add_tag),
                  MessageHandler(filters.Regex("^(all)$"), Tags.tags_all),
                  MessageHandler(filters.Regex("^(Save)$"), Tags.save_tag)],
            REMOVE: [MessageHandler(filters.Regex(r"^(?!all$|Save$)(#\w+)$"), Tags.remove_tag),
                     MessageHandler(filters.Regex("^(all)$"), Tags.tags_all),
                     MessageHandler(filters.Regex("^(Save)$"), Tags.save_tag)],

        },
        fallbacks=[CommandHandler("cancel", EventSaver.cancel)],

    )

    feedback_handler = ConversationHandler(
        entry_points=[CommandHandler("feedback", Feedback.feedback),
                      MessageHandler(filters.Regex("^(Anna palautetta|Give feedback)$"), Feedback.feedback)],
        states={
            Feedback.FEEDBACK: [MessageHandler(filters.TEXT & ~filters.COMMAND, Feedback.save_text)]
        },
        fallbacks=[CommandHandler("cancel", EventSaver.cancel)]
    )

    start_handler = ConversationHandler(
        entry_points=[CommandHandler("start", Start.start), CommandHandler("lang", Start.start),
                      MessageHandler(filters.Regex("^(Change language|Vaihda kieli)$"), Start.start)],
        states={
            Start.LANG: [MessageHandler(filters.TEXT & ~filters.COMMAND, Start.lang)]
        },
        fallbacks=[CommandHandler("cancel", EventSaver.cancel)]
    )

    dev_handler = ConversationHandler(
        entry_points=[CommandHandler("dev", Dev.dev), MessageHandler(filters.Regex("^(Secret menu|Salainen menu)$"), Dev.dev)],
        states={
            Dev.MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, Dev.menu)],
            Dev.ADD_TAGS: [MessageHandler(filters.TEXT & ~filters.COMMAND, Dev.add_tag)],
            Dev.REMOVE_TAGS: [MessageHandler(filters.TEXT & ~filters.COMMAND, Dev.remove_tag)],
            Dev.CHANGE_USER_TYPE_1: [MessageHandler(filters.TEXT & ~filters.COMMAND, Dev.check_for_user)],
            Dev.CHANGE_USER_TYPE_2: [MessageHandler(filters.TEXT & ~filters.COMMAND, Dev.set_user_type)],
        },
        fallbacks=[CommandHandler("cancel", EventSaver.cancel)]
    )
    list_handler = ConversationHandler(
        entry_points=[CommandHandler("list", List.list), MessageHandler(filters.Regex("^(List events|Listaa tapahtumat)$"), List.list)],
        states={
            List.MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, List.menu)],
            List.TAGS: [MessageHandler(filters.TEXT & ~filters.COMMAND, List.list_by_tags)],
            List.TIME_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, List.time_menu)],
        },
        fallbacks=[CommandHandler("cancel", EventSaver.cancel)]
    )





    application.add_handler(CommandHandler("menu", Menu.menu))

    application.add_handler(CommandHandler("accept", Accept.accept))
    application.add_handler(CommandHandler("help", Help.help))

    application.add_handler(CallbackQueryHandler(List.button))
    application.add_handler(list_handler)
    application.add_handler(start_handler)
    application.add_handler(event_handler)
    application.add_handler(edit_handler)
    application.add_handler(tag_handler)
    application.add_handler(dev_handler)
    application.add_handler(feedback_handler)



    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
