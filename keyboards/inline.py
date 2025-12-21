from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import CHANNEL_URL, ADMIN_USERNAME

def get_start_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("📢 Kanalga qo'shilish", url=CHANNEL_URL)],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_check_subscription_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("📢 Kanalga qo'shilish", url=CHANNEL_URL)],
        [InlineKeyboardButton("✅ Tekshirish", callback_data="check_subscription")],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_payment_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("💳 Karta yordamida to'lash", callback_data="pay_card")],
        [
            InlineKeyboardButton("⁉️ Yordam", url=f"https://t.me/{ADMIN_USERNAME.replace('@', '')}"),
            InlineKeyboardButton("🔍 To'lovlar tarix", callback_data="payment_history")
        ],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_to_payment_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("🔙 Orqaga", callback_data="back_to_payment")],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_admin_panel_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("📊 Statistika", callback_data="admin_stats")],
        [InlineKeyboardButton("💰 To'lovlar", callback_data="admin_payments")],
        [InlineKeyboardButton("📢 Reklama yuborish", callback_data="admin_broadcast")],
        [InlineKeyboardButton("🔍 Foydalanuvchi qidirish", callback_data="admin_search")],
        [InlineKeyboardButton("📥 Export", callback_data="admin_export")],
        [InlineKeyboardButton("👥 Adminlar", callback_data="admin_manage")],
        [InlineKeyboardButton("⚙️ Majburiy obuna", callback_data="admin_subscription")],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("🔙 Orqaga", callback_data="admin_back")],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_subscription_settings_keyboard(is_enabled: bool) -> InlineKeyboardMarkup:
    status_btn = InlineKeyboardButton(
        "❌ O'chirish" if is_enabled else "✅ Yoqish",
        callback_data="toggle_subscription"
    )
    keyboard = [
        [status_btn],
        [InlineKeyboardButton("📝 Kanal o'zgartirish", callback_data="change_channel")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="admin_back")],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_admin_manage_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("➕ Admin qo'shish", callback_data="add_admin")],
        [InlineKeyboardButton("➖ Admin o'chirish", callback_data="remove_admin")],
        [InlineKeyboardButton("📋 Adminlar ro'yxati", callback_data="list_admins")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="admin_back")],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_export_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("📄 CSV", callback_data="export_csv")],
        [InlineKeyboardButton("📊 Excel", callback_data="export_excel")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="admin_back")],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_cancel_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel_action")],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_payment_confirm_keyboard(payment_id: int) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"confirm_pay_{payment_id}"),
            InlineKeyboardButton("❌ Rad etish", callback_data=f"reject_pay_{payment_id}")
        ],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_pending_payments_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("📋 Kutilayotgan to'lovlar", callback_data="pending_payments")],
        [InlineKeyboardButton("📊 To'lov statistikasi", callback_data="payment_stats")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="admin_back")],
    ]
    return InlineKeyboardMarkup(keyboard)