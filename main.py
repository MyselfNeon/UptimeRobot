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
from info import ADMIN

# Explicitly add current directory to python path
sys.path.append(os.getcwd())

from MyselfNeon.monitor import monitor_task

async def start_bot():
    print("Starting Bot...")
    
    await start_web_server()
    await app.start()
    
    if ADMIN != 0:
        print(f"Sending startup message to: {ADMIN}")
        try:
            await app.send_message(
                ADMIN,
                "🎉 **Bot Restarted!**\n"
                "✅ **Monitoring Resumed.**"
            )
        except Exception as e:
            print(f"❌ Failed to send startup message: {e}")
    else:
        print("⚠️ ADMIN ID is 0. Set 'ADMIN' in env vars.")

    # Start Background Task
    asyncio.create_task(monitor_task(app))
    
    print("Bot is up and running!")
    await idle()
    await app.stop()

if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(start_bot())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Runtime Error: {e}")
        
