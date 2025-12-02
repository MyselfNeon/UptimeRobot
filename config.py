import os

# Get these from https://my.telegram.org
API_ID = int(os.environ.get("API_ID", ""))
API_HASH = os.environ.get("API_HASH", "")

# Get this from @BotFather
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# Your User ID (Get from @userinfobot)
ADMIN = int(os.environ.get("ADMIN", "841851780"))

# Server Port (Defaults to 8080 to satisfy cloud providers)
PORT = int(os.environ.get("PORT", "8080"))

# List of URLs to monitor
URLS = [
    "https://google.com",
    "https://github.com",
]

# How often to check in seconds
CHECK_INTERVAL = 60
