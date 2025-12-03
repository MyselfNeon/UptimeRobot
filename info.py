import os

# Get these from https://my.telegram.org
API_ID = int(os.environ.get("API_ID", ""))
API_HASH = os.environ.get("API_HASH", "")

# Get this from @BotFather
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# Your User ID (Get from @userinfobot)
ADMIN = int(os.environ.get("ADMIN", "841851780"))

# Server Port
PORT = int(os.environ.get("PORT", "8080"))

# Database Configuration
DB_URI = os.environ.get("DB_URI", "")
DB_NAME = os.environ.get("DB_NAME", "UptimeBot")

# Force Subscribe Channel ID (Default is the one you provided)
FORCE_SUB = os.environ.get("FORCE_SUB", "-1002384933640")
