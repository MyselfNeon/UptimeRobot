# ---------------------------------------------------
# File Name: Info.py
# Author: MyselfNeon
# GitHub: https://github.com/MyselfNeon/
# Telegram: https://t.me/MyelfNeon
# ---------------------------------------------------

import os

# Get these from https://my.telegram.org
API_ID = int(os.environ.get("API_ID", ""))
API_HASH = os.environ.get("API_HASH", "")

# Get this from @BotFather
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# Admin ID (For startup logs only)
ADMIN = int(os.environ.get("ADMIN", "0"))

# Server Port
PORT = int(os.environ.get("PORT", "8080"))

# Database Configuration
DB_URI = os.environ.get("DB_URI", "")
DB_NAME = os.environ.get("DB_NAME", "UptimeBot")
