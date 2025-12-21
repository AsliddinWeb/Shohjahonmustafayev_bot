import os
from dotenv import load_dotenv

load_dotenv()

# Bot token
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Owner (asosiy admin) - bu o'zgarmas
OWNER_ID = int(os.getenv("OWNER_ID"))

# Kanal
CHANNEL_ID = os.getenv("CHANNEL_ID")  # @username yoki -100xxxxxxxxxx
CHANNEL_URL = os.getenv("CHANNEL_URL")  # https://t.me/channel_name

# Yopiq kanal (to'lov qilganlar uchun)
PRIVATE_CHANNEL_URL = os.getenv("PRIVATE_CHANNEL_URL")

# Dumaloq video xabar
WELCOME_VIDEO_URL = "https://t.me/botkanal1234/2"

# Admin username (yordam uchun)
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")  # @admin_username

# To'lov summasi
PAYMENT_AMOUNT = 97000

# Database
DB_PATH = "bot.db"
