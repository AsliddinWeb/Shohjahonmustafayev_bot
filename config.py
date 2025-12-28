import os
from dotenv import load_dotenv

load_dotenv()

# Bot token
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Owner (asosiy admin)
OWNER_ID = int(os.getenv("OWNER_ID"))

# Kanal
CHANNEL_ID = os.getenv("CHANNEL_ID")
CHANNEL_URL = os.getenv("CHANNEL_URL")

# Yopiq kanal (to'lov qilganlar uchun)
PRIVATE_CHANNEL_URL = os.getenv("PRIVATE_CHANNEL_URL")
PRIVATE_CHANNEL_ID = int(os.getenv("PRIVATE_CHANNEL_ID"))

# Admin username (yordam uchun)
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")

# To'lov summasi
PAYMENT_AMOUNT = 47000

# Database
DB_PATH = "bot.db"