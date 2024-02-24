from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters, ContextTypes, \
    CallbackQueryHandler, CallbackContext

import Feedback
import EventSaver
import Start, Tags, MessageSender, Accept, Help, Edit, Dev, Menu, Cancel, Dictionary, Button, MyEvents, UserInfo
import Secrets

# Event states
ADD_REMOVE, ADD, REMOVE = range(3)

def main() -> None:
    application = Application.builder().token(Secrets.TOKEN).build()

    # Conversation handler for handling the creation of events
    event_handler = ConversationHandler(
        entry_points=[CommandHandler("event", EventSaver.event_command),
                      MessageHandler(filters.Regex("^(Luo tapahtuma|Create event)$"), EventSaver.event_command)],
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
            EventSaver.TAG_ADDING: [MessageHandler(filters.TEXT & ~filters.COMMAND, EventSaver.tag_adding)],
            EventSaver.TAG_REMOVING: [MessageHandler(filters.TEXT & ~filters.COMMAND, EventSaver.tag_removing)],
            EventSaver.SAVE_EVENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, EventSaver.save)],
        },
        fallbacks=[CommandHandler("cancel", EventSaver.cancel), MessageHandler(filters.COMMAND, Cancel.cancel)]
    )


    #convhandler for editing allready created events
    edit_handler = ConversationHandler(
        entry_points=[CommandHandler("edit", Edit.edit_command),
                      MessageHandler(filters.Regex("^(Edit event|Muokkaa tapahtumaa)$"), Edit.edit_command)],
        states={
            Edit.EVENT_SELECTOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, Edit.event_selector)],
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
            Edit.TAG_ADDING: [MessageHandler(filters.TEXT & ~filters.COMMAND, Edit.tags)],
            Edit.SUBMIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, Edit.submit)],
        },
        fallbacks=[CommandHandler("cancel", EventSaver.cancel), MessageHandler(filters.COMMAND, Cancel.cancel)],
    )

    # removing users
    user_info_handler = ConversationHandler(
        entry_points=[CommandHandler("userinfo", UserInfo.userinfo_command),
                      MessageHandler(filters.Regex("^(User settings|Käyttäjän asetukset)$"), UserInfo.userinfo_command)],
        states={
            UserInfo.ACTION_SELECTOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, UserInfo.action_selector)],
            UserInfo.DELETE_USER: [MessageHandler(filters.TEXT & ~filters.COMMAND, UserInfo.delete_user)],
            #UserInfo.USER_INFO: [MessageHandler(filters.TEXT & ~filters.COMMAND, UserInfo.)],
            UserInfo.LANG: [MessageHandler(filters.TEXT & ~filters.COMMAND, UserInfo.change_languange)],
        },
        fallbacks=[CommandHandler("cancel", EventSaver.cancel), MessageHandler(filters.COMMAND, Cancel.cancel)]
    )


    # To handle user adding tags
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
        fallbacks=[CommandHandler("cancel", EventSaver.cancel), MessageHandler(filters.COMMAND, Cancel.cancel)],
    )

    feedback_handler = ConversationHandler(
        entry_points=[CommandHandler("feedback", Feedback.feedback),
                      MessageHandler(filters.Regex("^(Anna palautetta|Give feedback)$"), Feedback.feedback)],
        states={
            Feedback.FEEDBACK: [MessageHandler(filters.TEXT & ~filters.COMMAND, Feedback.save_text)]
        },
        fallbacks=[CommandHandler("cancel", EventSaver.cancel), MessageHandler(filters.COMMAND, Cancel.cancel)]
    )

    start_handler = ConversationHandler(
        entry_points=[CommandHandler("start", Start.start), CommandHandler("lang", Start.start),

                      MessageHandler(filters.Regex("^(Change language|Vaihda kieli)$"), Start.start)],
        states={
            Start.LANG: [MessageHandler(filters.TEXT & ~filters.COMMAND, Start.lang)],
            Start.DATA_COLLECTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, Start.data_collection)]
        },
        fallbacks=[CommandHandler("cancel", EventSaver.cancel), MessageHandler(filters.COMMAND, Cancel.cancel)]
    )

    #secret keyboard for super admins
    dev_handler = ConversationHandler(
        entry_points=[CommandHandler("dev", Dev.dev), MessageHandler(filters.Regex("^(Secret menu|Salainen menu)$"), Dev.dev)],
        states={
            Dev.MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, Dev.menu)],
            Dev.SEND_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, Dev.send_message)],
            Dev.ADD_TAGS: [MessageHandler(filters.TEXT & ~filters.COMMAND, Dev.add_tag)],
            Dev.REMOVE_TAGS: [MessageHandler(filters.TEXT & ~filters.COMMAND, Dev.remove_tag)],
            Dev.CHANGE_USER_TYPE_1: [MessageHandler(filters.TEXT & ~filters.COMMAND, Dev.check_for_user)],
            Dev.CHANGE_USER_TYPE_2: [MessageHandler(filters.TEXT & ~filters.COMMAND, Dev.set_user_type)],
            Dev.LIST_USERS: [MessageHandler(filters.TEXT & ~filters.COMMAND, Dev.list_users)],
        },
        fallbacks=[CommandHandler("cancel", EventSaver.cancel), MessageHandler(filters.COMMAND, Cancel.cancel)]
    )

    #handles user query for events
    list_handler = ConversationHandler(
        entry_points=[CommandHandler("list", MessageSender.list),
                      MessageHandler(filters.Regex("^(List events|Listaa tapahtumat)$"), MessageSender.list)],
        states={
            MessageSender.MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, MessageSender.menu)],
            MessageSender.TAGS: [MessageHandler(filters.TEXT & ~filters.COMMAND, MessageSender.list_by_tags)],
            MessageSender.TIME_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, MessageSender.time_menu)],
        },
        fallbacks=[CommandHandler("cancel", EventSaver.cancel), MessageHandler(filters.COMMAND, Cancel.cancel)]
    )

    #handles admins accepting events
    accept_handler = ConversationHandler(
        entry_points=[CommandHandler("Accept", Accept.accept),
                      MessageHandler(filters.Regex("^(Hyväksy tapahtumia|Accept events)$"), Accept.accept)],
        states={
            Accept.EVENT_SELECTOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, Accept.event_selector)],
            Accept.DECISION: [MessageHandler(filters.TEXT & ~filters.COMMAND, Accept.decision)],
            Accept.REPLY: [MessageHandler(filters.TEXT & ~filters.COMMAND, Accept.reply)],
        },
        fallbacks=[CommandHandler("cancel", EventSaver.cancel), MessageHandler(filters.COMMAND, Cancel.cancel)]
    )

    my_events_handler = ConversationHandler(
        entry_points=[CommandHandler("get_events", MyEvents.menu),
                      MessageHandler(filters.Regex("^(Näytä omat tapahtumat|Show my events)$"), MyEvents.menu)],
        states={
            MyEvents.CHOICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, MyEvents.choice)],

        },
        fallbacks=[CommandHandler("cancel", EventSaver.cancel), MessageHandler(filters.COMMAND, Cancel.cancel)]
    )


    message_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, Dictionary.BasicHandler)


    application.add_handler(CallbackQueryHandler(Button.button))
    application.add_handler(accept_handler, 1)
    application.add_handler(list_handler, 2)
    application.add_handler(start_handler, 3)
    application.add_handler(event_handler, 4)
    application.add_handler(edit_handler, 5)
    application.add_handler(tag_handler, 6)
    application.add_handler(dev_handler, 7)
    application.add_handler(feedback_handler, 8)
    application.add_handler(my_events_handler, 10)
    application.add_handler(user_info_handler, 11)


    application.add_handler(CommandHandler("menu", Menu.menu), 0)
    application.add_handler(CommandHandler("accept", Accept.accept), 0)
    application.add_handler(CommandHandler("help", Help.help), 0)
    application.add_handler(message_handler)



    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
