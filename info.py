# ---------------------------------------------------
# File Name: info.py
# ---------------------------------------------------
import os

# Get these from https://my.telegram.org
API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")

# Get this from @BotFather
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# Admin ID (For startup logs and restricted commands)
# Reads from ENV; defaults to 0 if not set.
ADMIN = int(os.environ.get("ADMIN", "0"))

# Server Port
PORT = int(os.environ.get("PORT", "8080"))

# Database Configuration
DB_URI = os.environ.get("DB_URI", "")
DB_NAME = os.environ.get("DB_NAME", "UptimeBot")
