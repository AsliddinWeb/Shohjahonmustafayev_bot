from telegram import Update
from telegram.ext import ContextTypes
from services.user_service import add_user
from services.payment_service import create_payment, get_user_payments, has_confirmed_payment
from keyboards.inline import get_payment_keyboard, get_back_to_payment_keyboard
from config import PAYMENT_AMOUNT, PRIVATE_CHANNEL_URL, OWNER_ID
from services.admin_service import is_admin

WELCOME_VIDEO_MSG_ID = 2  # https://t.me/botkanal1234/2
WELCOME_VIDEO_CHAT = "@botkanal1234"  # Kanal username


CARD_TEXT = """
💳 <b>To'lov qilish</b>

Pastda to'lov qilishingiz uchun karta raqamlari 👇

Uzcard: <code>5614 6829 0443 5965</code>  
👤 Mustafayev Shohjahon  
📞 Kartaga ulangan raqam: <code>90 872 24 10</code>

Humo: <code>4198 1300 4859 6778</code>  
👤 Sarvar Xasanov

💵 <b>To'lovni amalga oshirgandan so‘ng</b> chek (screenshot)ni shu yerga yuboring.

⚠️ Screeshotda sana, to'lov summasi va to'lov vaqti ko‘rinishi shart.
"""


PAYMENT_RECEIVED_TEXT = """
✅ <b>To'lov ma'lumotlari adminga yuborildi!</b>

Adminlar tasdiqlashi bilan bot orqali sizga yopiq kanalga kirish uchun link beriladi.

⏳ Iltimos, kuting...
"""

PAYMENT_HISTORY_TEXT = """
📋 <b>Sizning to'lovlaringiz:</b>

{history}
"""

# Welcome
WELCOME_PHOTO = "assets/welcome.jpg"

WELCOME_TEXT = """
🎉 <b>Tabriklaymiz!</b>

Siz <b>“2026-yilga Qadam”</b> masterklassiga ro‘yxatdan o‘tdingiz.

🧠 So‘nggi 4 yildan beri xotira va miya rivoji bilan shug‘ullanaman.

🏆 <b>Mening natijalarim:</b>
- Eslab qolish bo‘yicha jahon reytingida <b>TOP–22</b>
- Minglab insonlarga super xotira va maqsad qo‘yishda yordam berganman
- “Super 30 kun” kundaligi va cheklistlar muallifiman

🚀 <b>“2026-yilga Qadam” masterklassi:</b>
📆 1 haftalik intensiv trening
🎯 2026-yil uchun aniq maqsadlar tuzish
🧠 Tez va oson natija beradigan usullar

❗ <b>Masterklass minimal narxda</b>, lekin qiymati juda yuqori.

🎁 <b>Bonuslar:</b>
- Yopiq Telegram kanal
- “Super 30 kun” kundaligi

🔥 Siz bu yerga 2026-yilda maqsadlaringizga erishish uchun keldingiz.
Oxirigacha harakat qiling va bizning safimizga qo‘shiling!

👇 <b>Boshlash uchun havola orqali o‘ting.</b>
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
    try:
        await update.message.reply_photo(
            photo=open(WELCOME_PHOTO, 'rb'),
            caption=WELCOME_TEXT,
            parse_mode='HTML',
            reply_markup=get_payment_keyboard()
        )
    except FileNotFoundError:
        await update.message.reply_text(
            text=WELCOME_TEXT,
            parse_mode='HTML',
        )

    # # To'lov xabari
    # await update.message.reply_text(
    #     text=PAYMENT_TEXT.format(amount=PAYMENT_AMOUNT),
    #     parse_mode='HTML',
    #     reply_markup=get_payment_keyboard()
    # )


async def pay_card_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data['state'] = 'waiting_screenshot'

    # avval xabarning o'zini o'chiramiz
    try:
        await query.message.delete()
    except Exception as e:
        print("delete error:", e)

    # yangi text yuboramiz
    await query.message.chat.send_message(
        text=CARD_TEXT,
        parse_mode='HTML',
        reply_markup=get_back_to_payment_keyboard()
    )


async def back_to_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data.clear()

    # eski xabarni o‘chir
    try:
        await query.message.delete()
    except:
        pass

    # Welcome xabar
    try:
        await query.message.chat.send_photo(
            photo=open(WELCOME_PHOTO, 'rb'),
            caption=WELCOME_TEXT,
            parse_mode='HTML',
            reply_markup=get_payment_keyboard()
        )
    except FileNotFoundError:
        await query.message.chat.send_message(
            text=WELCOME_TEXT,
            parse_mode='HTML',
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
            }.get(payment['status'], 'Nomaʼlum')

            history += f"{i}. {status_emoji} {payment['amount']:,.0f} so'm - {status_text}\n   📅 {payment['created_at']}\n\n".replace(",", " ")

    # avval media xabarlarni o'chiramiz
    try:
        await query.message.delete()
    except:
        pass

    await query.message.chat.send_message(
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