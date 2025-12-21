from telegram import Update
from telegram.ext import ContextTypes
from middlewares.admin_check import admin_required_callback
from keyboards.inline import get_pending_payments_keyboard, get_back_keyboard
from services.payment_service import (
    get_payment,
    get_pending_payments,
    confirm_payment,
    reject_payment,
    get_payment_stats
)
from services.user_service import get_user
from config import PRIVATE_CHANNEL_ID


@admin_required_callback
async def admin_payments_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.message.edit_text(
        text="💰 <b>To'lovlar boshqaruvi</b>\n\nQuyidagi bo'limlardan birini tanlang:",
        parse_mode='HTML',
        reply_markup=get_pending_payments_keyboard()
    )


@admin_required_callback
async def pending_payments_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    payments = await get_pending_payments()

    if not payments:
        await query.message.edit_text(
            text="✅ Kutilayotgan to'lovlar yo'q!",
            parse_mode='HTML',
            reply_markup=get_back_keyboard()
        )
        return

    text = f"⏳ <b>Kutilayotgan to'lovlar:</b> {len(payments)} ta\n\n"

    for payment in payments[:10]:
        user = await get_user(payment['chat_id'])
        username = f"@{user['username']}" if user and user['username'] else "-"

        text += (
            f"🆔 #{payment['id']} | 👤 <code>{payment['chat_id']}</code> | {username}\n"
            f"💰 {payment['amount']:,} so'm | 📅 {payment['created_at']}\n\n"
        ).replace(",", " ")

    if len(payments) > 10:
        text += f"... va yana {len(payments) - 10} ta"

    await query.message.edit_text(
        text=text,
        parse_mode='HTML',
        reply_markup=get_back_keyboard()
    )


@admin_required_callback
async def payment_stats_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    stats = await get_payment_stats()

    text = f"""
📊 <b>To'lovlar statistikasi</b>

📋 Jami to'lovlar: <b>{stats['total']}</b> ta
✅ Tasdiqlangan: <b>{stats['confirmed']}</b> ta
⏳ Kutilayotgan: <b>{stats['pending']}</b> ta
❌ Rad etilgan: <b>{stats['rejected']}</b> ta

💰 Jami summa: <b>{stats['total_amount']:,}</b> so'm
""".replace(",", " ")

    await query.message.edit_text(
        text=text,
        parse_mode='HTML',
        reply_markup=get_back_keyboard()
    )


async def confirm_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    payment_id = int(query.data.split("_")[-1])
    admin_id = query.from_user.id

    # To'lovni tasdiqlash
    result = await confirm_payment(payment_id, admin_id)

    if not result:
        await query.answer("❌ Bu to'lov allaqachon ko'rib chiqilgan!", show_alert=True)
        return

    # Payment ma'lumotlarini olish
    payment = await get_payment(payment_id)
    user_chat_id = payment['chat_id']

    # Bir martalik invite link yaratish
    try:
        invite = await context.bot.create_chat_invite_link(
            chat_id=PRIVATE_CHANNEL_ID,
            member_limit=1
        )
        invite_link = invite.invite_link
    except Exception as e:
        print(f"Invite link yaratishda xato: {e}")
        invite_link = None

    # Foydalanuvchiga xabar yuborish
    if invite_link:
        try:
            await context.bot.send_message(
                chat_id=user_chat_id,
                text=f"🎉 <b>Tabriklaymiz!</b>\n\n"
                     f"Sizning to'lovingiz tasdiqlandi!\n\n"
                     f"🔗 Yopiq kanalga kirish uchun link:\n{invite_link}\n\n"
                     f"⚠️ Link faqat bir martalik!",
                parse_mode='HTML'
            )
        except Exception as e:
            print(f"Foydalanuvchiga xabar yuborishda xato: {e}")
    else:
        try:
            await context.bot.send_message(
                chat_id=user_chat_id,
                text="🎉 <b>Tabriklaymiz!</b>\n\n"
                     "Sizning to'lovingiz tasdiqlandi!\n\n"
                     "⚠️ Admin siz bilan tez orada bog'lanadi.",
                parse_mode='HTML'
            )
        except Exception as e:
            print(f"Foydalanuvchiga xabar yuborishda xato: {e}")

    await query.answer("✅ To'lov tasdiqlandi!", show_alert=True)

    # Xabarni yangilash
    await query.message.edit_caption(
        caption=query.message.caption + f"\n\n✅ <b>TASDIQLANDI</b>\n👤 Admin: <code>{admin_id}</code>",
        parse_mode='HTML'
    )


async def reject_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    payment_id = int(query.data.split("_")[-1])
    admin_id = query.from_user.id

    # To'lovni rad etish
    result = await reject_payment(payment_id, admin_id)

    if not result:
        await query.answer("❌ Bu to'lov allaqachon ko'rib chiqilgan!", show_alert=True)
        return

    # Payment ma'lumotlarini olish
    payment = await get_payment(payment_id)
    user_chat_id = payment['chat_id']

    # Foydalanuvchiga xabar yuborish
    try:
        await context.bot.send_message(
            chat_id=user_chat_id,
            text="❌ <b>Kechirasiz!</b>\n\n"
                 "Sizning to'lovingiz rad etildi.\n\n"
                 "Agar xatolik bo'lsa, admin bilan bog'laning.",
            parse_mode='HTML'
        )
    except Exception as e:
        print(f"Foydalanuvchiga xabar yuborishda xato: {e}")

    await query.answer("❌ To'lov rad etildi!", show_alert=True)

    # Xabarni yangilash
    await query.message.edit_caption(
        caption=query.message.caption + f"\n\n❌ <b>RAD ETILDI</b>\n👤 Admin: <code>{admin_id}</code>",
        parse_mode='HTML'
    )