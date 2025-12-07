# ---------------------------------------------------
# File Name: Main.py
# Author: MyselfNeon
# GitHub: https://github.com/MyselfNeon/
# Telegram: https://t.me/MyelfNeon
# ---------------------------------------------------

import sys
import os
import asyncio
from pyrogram import idle
from app import app, start_web_server

# Explicitly add current directory to python path
sys.path.append(os.getcwd())

from MyselfNeon.monitor import monitor_task

async def start_bot():
    print("Starting Bot...")
    
    await start_web_server()
    
    await app.start()
    
    # Replace your numeric Telegram ID
    OWNER_ID = 841851780
    
    if OWNER_ID != 0:
        print(f"Sending startup message to: {OWNER_ID}")
        try:
            await app.send_message(
                OWNER_ID,
                "🎉 **__Bot Successfully Restarted !!__**\n\n"
                "✅ **__Systems are back Online.__**\n"
                "✅ **__All Monitorings are now Resumed.__**"
            )
            print("✅ Startup message sent.")
        except Exception as e:
            print(f"❌ Failed to send startup message: {e}")
            print("💡 Hint: Make sure you have started the bot in private.")
    else:
        print("⚠️ OWNER_ID is 0. Skipping startup message. Edit main.py to fix this.")

    # 3. Start Background Task
    asyncio.create_task(monitor_task(app))
    
    print("Bot is up and running!")
    await idle()
    
    await app.stop()
    print("Bot Stopped.")

if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(start_bot())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Runtime Error: {e}")
