from telegram import Update
from telegram.ext import ContextTypes
from services.user_service import add_user
from services.payment_service import create_payment, get_user_payments, has_confirmed_payment
from keyboards.inline import get_payment_keyboard, get_back_to_payment_keyboard
from config import PAYMENT_AMOUNT, PRIVATE_CHANNEL_URL, OWNER_ID


WELCOME_TEXT = """
🎉 <b>Tabriklaymiz!</b>

Siz <b>"2026-yilga Qadam"</b> masterklassiga ro'yxatdan o'tdingiz.

So'nggi 4 yildan beri xotira kuchaytirish va shaxsiy rivojlanish bilan shug'ullanaman.

🧠 Eslab qolish bo'yicha jahon reytingida <b>TOP–22</b> natijaga erishganman.
📘 <b>"Super 30 kun"</b> kundaligi va cheklistlar muallifiman.
👥 Minglab insonlarga kuchli xotira va aniq maqsad qo'yishda yordam berganman.

🚀 <b>"2026-yilga Qadam"</b> —
📆 1 haftalik intensiv masterklass
🎯 2026-yil uchun aniq maqsadlar
🧠 Tez va oson natija beradigan usullar

❗ Masterklass minimal summada, lekin qiymati juda yuqori.

🔥 Siz bu yerga 2026-yilda maqsadlaringizga erishish uchun keldingiz.
Oxirigacha harakat qiling va bizning safimizga qo'shiling!

👇 <b>Boshlash uchun pastdagi tugmani bosing.</b>
"""

CARD_TEXT = """
💳 <b>To'lov qilish</b>

Pastda to'lov qilishingiz uchun karta raqamlari 👇

<b>Uzcard:</b> <code>5614 6829 0443 5965</code>
👤 Mustafayev Shohjahon
📞 Kartaga ulangan raqam: <code>90 872 24 10</code>

<b>Humo:</b> <code>4198 1300 4859 6778</code>
👤 Sarvar Xasanov

💵 <b>To'lov summasi:</b> {amount:,} so'm

✅ To'lovni amalga oshirgandan so'ng chek (screenshot)ni shu yerga yuboring.

⚠️ Screenshotda sana, to'lov summasi va to'lov vaqti ko'rinishi shart.
""".replace(",", " ")

PAYMENT_RECEIVED_TEXT = """
✅ <b>To'lov ma'lumotlari adminga yuborildi!</b>

Adminlar tasdiqlashi bilan bot orqali sizga yopiq kanalga kirish uchun link beriladi.

⏳ Iltimos, kuting...
"""

PAYMENT_HISTORY_TEXT = """
📋 <b>Sizning to'lovlaringiz:</b>

{history}
"""


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    # Userni bazaga saqlash
    await add_user(
        chat_id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username
    )

    # Agar to'lov tasdiqlangan bo'lsa
    if await has_confirmed_payment(user.id):
        await update.message.reply_text(
            text=f"✅ Siz allaqachon to'lov qilgansiz!\n\n🔗 Yopiq kanal: {PRIVATE_CHANNEL_URL}",
            parse_mode='HTML'
        )
        return

    # State ni tozalash
    context.user_data.clear()

    # Welcome xabar
    await update.message.reply_text(
        text=WELCOME_TEXT,
        parse_mode='HTML',
        reply_markup=get_payment_keyboard()
    )


async def pay_card_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data['state'] = 'waiting_screenshot'

    await query.message.edit_text(
        text=CARD_TEXT.format(amount=PAYMENT_AMOUNT),
        parse_mode='HTML',
        reply_markup=get_back_to_payment_keyboard()
    )


async def back_to_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data.clear()

    await query.message.edit_text(
        text=WELCOME_TEXT,
        parse_mode='HTML',
        reply_markup=get_payment_keyboard()
    )


async def payment_history_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    payments = await get_user_payments(user_id)

    if not payments:
        history = "❌ Sizda hali to'lovlar yo'q."
    else:
        history = ""
        for i, payment in enumerate(payments, 1):
            status_emoji = {
                'pending': '⏳',
                'confirmed': '✅',
                'rejected': '❌'
            }.get(payment['status'], '❓')

            status_text = {
                'pending': 'Kutilmoqda',
                'confirmed': 'Tasdiqlangan',
                'rejected': 'Rad etilgan'
            }.get(payment['status'], "Noma'lum")

            history += f"{i}. {status_emoji} {payment['amount']:,} so'm - {status_text}\n   📅 {payment['created_at']}\n\n".replace(",", " ")

    await query.message.edit_text(
        text=PAYMENT_HISTORY_TEXT.format(history=history),
        parse_mode='HTML',
        reply_markup=get_back_to_payment_keyboard()
    )


async def receive_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('state') != 'waiting_screenshot':
        return

    user = update.effective_user

    # Rasm borligini tekshirish
    if not update.message.photo:
        await update.message.reply_text(
            text="❌ Iltimos, to'lov cheki <b>rasmini</b> yuboring!",
            parse_mode='HTML'
        )
        return

    # Rasmni olish
    photo = update.message.photo[-1]
    file_id = photo.file_id

    # To'lovni bazaga saqlash
    payment_id = await create_payment(
        chat_id=user.id,
        screenshot_file_id=file_id,
        amount=PAYMENT_AMOUNT
    )

    # Foydalanuvchiga xabar
    await update.message.reply_text(
        text=PAYMENT_RECEIVED_TEXT,
        parse_mode='HTML'
    )

    # Adminlarga xabar yuborish
    from keyboards.inline import get_payment_confirm_keyboard
    from services.admin_service import get_all_admins

    admin_text = f"""
🆕 <b>Yangi to'lov!</b>

👤 <b>Foydalanuvchi:</b>
- ID: <code>{user.id}</code>
- Ism: {user.first_name or '-'}
- Username: @{user.username or '-'}

💰 <b>Summa:</b> {PAYMENT_AMOUNT:,} so'm
🆔 <b>To'lov ID:</b> #{payment_id}
""".replace(",", " ")

    # Owner ga yuborish
    try:
        await context.bot.send_photo(
            chat_id=OWNER_ID,
            photo=file_id,
            caption=admin_text,
            parse_mode='HTML',
            reply_markup=get_payment_confirm_keyboard(payment_id)
        )
    except Exception as e:
        print(f"Owner ga yuborishda xato: {e}")

    # Boshqa adminlarga yuborish
    admins = await get_all_admins()
    for admin in admins:
        try:
            await context.bot.send_photo(
                chat_id=admin['chat_id'],
                photo=file_id,
                caption=admin_text,
                parse_mode='HTML',
                reply_markup=get_payment_confirm_keyboard(payment_id)
            )
        except Exception as e:
            print(f"Admin {admin['chat_id']} ga yuborishda xato: {e}")

    context.user_data.clear()