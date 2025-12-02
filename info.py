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
    "https://saverestrictions-bot.onrender.com/",
    "https://website-monitor-ddy2.onrender.com/",
    "https://telegraph-bot-q90q.onrender.com/",
    "https://filestream-bot-njtx.onrender.com/",
    "https://saverestrictions-bot.onrender.com/",
    "https://filestore-bot-x4iy.onrender.com/",
    "https://neonfilter-bot-ume4.onrender.com/",
    "https://session-generator-bot-iq7n.onrender.com/",
    "https://uptimerobot-oq3h.onrender.com",
    "https://telegraph-bot-q90q.onrender.com/",
]

# How often to check in seconds
CHECK_INTERVAL = 60
