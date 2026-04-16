# --- info.py ---
import os

# Get these from https://my.telegram.org
API_ID = int(os.environ.get("API_ID", ""))
API_HASH = os.environ.get("API_HASH", "")

# Get this from @BotFather
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# Admin ID (For startup logs and restricted commands)
ADMIN = int(os.environ.get("ADMIN", "841851780"))

# Server Port
PORT = int(os.environ.get("PORT", "8080"))

# Database Configuration
DB_URI = os.environ.get("DB_URI", "")
DB_NAME = os.environ.get("DB_NAME", "UptimeBot")

# Keep Alive Configuration
KEEP_ALIVE_URL = os.environ.get("KEEP_ALIVE_URL", "/").strip()

# Channel Status Configuration
STATUS_UPDATE_INTERVAL = int(os.environ.get("STATUS_UPDATE_INTERVAL", "300"))
