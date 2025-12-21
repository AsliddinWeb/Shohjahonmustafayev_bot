from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)

from config import BOT_TOKEN
from database.models import create_tables

# Handlers
from handlers.start import (
    start_command,
    pay_card_callback,
    back_to_payment_callback,
    payment_history_callback,
    receive_screenshot
)
from handlers.admin_panel import admin_command, admin_back_callback, cancel_action_callback
from handlers.statistics import stats_callback
from handlers.broadcast import broadcast_callback, receive_broadcast_content
from handlers.user_search import search_callback, receive_search_query
from handlers.export import export_callback, export_csv_callback, export_excel_callback
from handlers.admin_manage import (
    admin_manage_callback,
    add_admin_callback,
    remove_admin_callback,
    list_admins_callback,
    receive_add_admin,
    receive_remove_admin
)
from handlers.subscription import (
    subscription_settings_callback,
    toggle_subscription_callback,
    change_channel_callback,
    receive_channel_id
)
from handlers.payment import (
    admin_payments_callback,
    pending_payments_callback,
    payment_stats_callback,
    confirm_payment_callback,
    reject_payment_callback
)


async def post_init(application: Application):
    """Bot ishga tushganda database yaratish"""
    await create_tables()
    print("✅ Database tayyor!")


def main():
    # Bot yaratish
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()

    # Command handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("admin", admin_command))

    # Start / Payment callbacks
    app.add_handler(CallbackQueryHandler(pay_card_callback, pattern="^pay_card$"))
    app.add_handler(CallbackQueryHandler(back_to_payment_callback, pattern="^back_to_payment$"))
    app.add_handler(CallbackQueryHandler(payment_history_callback, pattern="^payment_history$"))

    # Admin panel callbacks
    app.add_handler(CallbackQueryHandler(admin_back_callback, pattern="^admin_back$"))
    app.add_handler(CallbackQueryHandler(cancel_action_callback, pattern="^cancel_action$"))
    app.add_handler(CallbackQueryHandler(stats_callback, pattern="^admin_stats$"))
    app.add_handler(CallbackQueryHandler(export_callback, pattern="^admin_export$"))
    app.add_handler(CallbackQueryHandler(export_csv_callback, pattern="^export_csv$"))
    app.add_handler(CallbackQueryHandler(export_excel_callback, pattern="^export_excel$"))
    app.add_handler(CallbackQueryHandler(admin_manage_callback, pattern="^admin_manage$"))
    app.add_handler(CallbackQueryHandler(list_admins_callback, pattern="^list_admins$"))
    app.add_handler(CallbackQueryHandler(subscription_settings_callback, pattern="^admin_subscription$"))
    app.add_handler(CallbackQueryHandler(toggle_subscription_callback, pattern="^toggle_subscription$"))

    # Admin payments callbacks
    app.add_handler(CallbackQueryHandler(admin_payments_callback, pattern="^admin_payments$"))
    app.add_handler(CallbackQueryHandler(pending_payments_callback, pattern="^pending_payments$"))
    app.add_handler(CallbackQueryHandler(payment_stats_callback, pattern="^payment_stats$"))
    app.add_handler(CallbackQueryHandler(confirm_payment_callback, pattern=r"^confirm_pay_\d+$"))
    app.add_handler(CallbackQueryHandler(reject_payment_callback, pattern=r"^reject_pay_\d+$"))

    # Broadcast
    app.add_handler(CallbackQueryHandler(broadcast_callback, pattern="^admin_broadcast$"))

    # Search
    app.add_handler(CallbackQueryHandler(search_callback, pattern="^admin_search$"))

    # Admin manage
    app.add_handler(CallbackQueryHandler(add_admin_callback, pattern="^add_admin$"))
    app.add_handler(CallbackQueryHandler(remove_admin_callback, pattern="^remove_admin$"))

    # Channel change
    app.add_handler(CallbackQueryHandler(change_channel_callback, pattern="^change_channel$"))

    # Message handlers
    app.add_handler(MessageHandler(
        filters.PHOTO & filters.ChatType.PRIVATE,
        handle_photo_messages
    ))

    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE,
        handle_text_messages
    ))

    print("✅ Bot ishga tushdi!")

    # Bot ishga tushirish
    app.run_polling(drop_pending_updates=True)


async def handle_photo_messages(update, context):
    """Rasm xabarlarni handle qilish"""
    state = context.user_data.get('state')

    if state == 'waiting_screenshot':
        await receive_screenshot(update, context)


async def handle_text_messages(update, context):
    """Text xabarlarni state bo'yicha yo'naltirish"""
    state = context.user_data.get('state')

    if state == 'waiting_broadcast':
        await receive_broadcast_content(update, context)
    elif state == 'waiting_search':
        await receive_search_query(update, context)
    elif state == 'waiting_add_admin':
        await receive_add_admin(update, context)
    elif state == 'waiting_remove_admin':
        await receive_remove_admin(update, context)
    elif state == 'waiting_channel_id':
        await receive_channel_id(update, context)
    elif state == 'waiting_screenshot':
        await update.message.reply_text(
            text="❌ Iltimos, to'lov cheki <b>rasmini</b> yuboring!",
            parse_mode='HTML'
        )


if __name__ == "__main__":
    main()