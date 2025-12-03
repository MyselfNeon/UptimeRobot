import os

# Get these from https://my.telegram.org
API_ID = int(os.environ.get("API_ID", ""))
API_HASH = os.environ.get("API_HASH", "")

# Get this from @BotFather
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# Your User ID (Get from @userinfobot)
ADMIN = int(os.environ.get("ADMIN", "841851780"))

# Authorized Users (Separate multiple IDs with commas, e.g., "12345,67890")
auth_users_raw = os.environ.get("AUTH_USERS", "")
AUTH_USERS = {int(x) for x in auth_users_raw.split(",") if x.strip()}
AUTH_USERS.add(ADMIN) # Ensure Admin is always authorized

# Server Port
PORT = int(os.environ.get("PORT", "8080"))

# Database Configuration
DB_URI = os.environ.get("DB_URI", "")
DB_NAME = os.environ.get("DB_NAME", "UptimeBot")
