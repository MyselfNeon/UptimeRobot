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
    
    # 1. Start Web Server
    await start_web_server()
    
    # 2. Start Telegram Client
    await app.start()
    print("Telegram Client Started.")
    
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
